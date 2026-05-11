from typing import List, Dict, Any, Optional, Union

import pandas as pd

from .filters import FilterBuilder
from .mappers import DataFrameMapper
from .models import ExperimentRecord, VersionInfo
from .services.dataset import DatasetService
from .services.version import VersionService
from .transport import Transport, RequestsTransport


class ElectrospinningDataClient:
    """
    Main client for interacting with the Electrospinning Data Public API.
    Provides methods for downloading datasets, listing versions, and 
    exporting data.
    """

    def __init__(
        self,
        base_url: str = "https://api.electrospinning-data.org/public/dataset",
        transport: Optional[Transport] = None,
        timeout: int = 60,
        verify: bool = True
    ):
        """
        Initialize the Electrospinning Hub API client.

        Args:
            base_url: The base URL of the public API.
            transport: Custom HTTP transport implementation.
            timeout: Default request timeout in seconds.
            verify: Whether to verify SSL certificates.
        """
        self.base_url = base_url.rstrip("/")
        self.transport = transport or RequestsTransport(
            timeout=timeout, verify=verify
        )

        # Internal services
        self._dataset_service = DatasetService(self.transport, self.base_url)
        self._version_service = VersionService(self.transport, self.base_url)

    def download_latest(
        self,
        filters: Optional[Union[Dict[str, Any], FilterBuilder]] = None
    ) -> pd.DataFrame:
        """
        Download the most recent dataset snapshot as a pandas DataFrame.

        Args:
            filters: Optional filters to apply to the dataset.

        Returns:
            A pandas DataFrame containing the flattened records.
        """
        records = self._dataset_service.get_records(
            version="latest", filters=filters
        )
        return self._to_dataframe(records)

    def download_version(
        self,
        version: str,
        filters: Optional[Union[Dict[str, Any], FilterBuilder]] = None
    ) -> pd.DataFrame:
        """
        Download a specific dataset version snapshot as a pandas DataFrame.

        Args:
            version: Version identifier (e.g., 'v1.0.0').
            filters: Optional filters to apply to the dataset.

        Returns:
            A pandas DataFrame containing the flattened records.
        """
        records = self._dataset_service.get_records(
            version=version, filters=filters
        )
        return self._to_dataframe(records)

    def get_versions(self) -> List[VersionInfo]:
        """
        Retrieve a list of all available dataset version snapshots.

        Returns:
            A list of VersionInfo objects.
        """
        return self._version_service.list_versions()

    def export_file(
        self,
        output_path: str,
        export_format: str = "xlsx",
        version: str = "latest",
        filters: Optional[Union[Dict[str, Any], FilterBuilder]] = None
    ) -> None:
        """
        Export the dataset (optionally filtered) directly to a local file.

        Args:
            output_path: Local destination path for the exported file.
            export_format: File format ('xlsx', 'json', 'zip').
            version: Dataset version to export.
            filters: Optional filters.
        """
        self._dataset_service.export(
            output_path,
            export_format=export_format,
            version=version,
            filters=filters
        )

    def load_records(
        self,
        skip: int = 0,
        limit: int = 100,
        version: str = "latest",
        filters: Optional[Union[Dict[str, Any], FilterBuilder]] = None
    ) -> Dict[str, Any]:
        """
        Fetch a paginated slice of records in raw dictionary format.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            version: Dataset version.
            filters: Optional filters.

        Returns:
            A dictionary containing the paginated data and metadata.
        """
        return self._dataset_service.load_paginated(
            skip=skip,
            limit=limit,
            version=version,
            filters=filters
        )

    def close(self) -> None:
        """Close the underlying transport and release resources."""
        if hasattr(self.transport, 'close'):
            self.transport.close()

    def _to_dataframe(self, records: List[ExperimentRecord]) -> pd.DataFrame:
        """Convert a list of records to a flattened pandas DataFrame."""
        if not records:
            return pd.DataFrame()

        flattened_data = DataFrameMapper.map_records(records)
        df = pd.DataFrame(flattened_data)

        # Apply robust type coercion for numeric columns
        numeric_cols = [
            'solution_concentration', 'solution_viscosity',
            'solution_surface_tension', 'solution_conductivity',
            'solution_evaporation_rate', 'voltage', 'flow_rate',
            'tip_collector_distance', 'spinning_duration',
            'temperature', 'humidity', 'fiber_diameter',
            'fiber_diameter_variation', 'tensile_strength',
            'modulus', 'elongation_at_break', 'surface_area',
            'porosity', 'permeability'
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Cleanup: Standardize missing values
        df = df.mask(df == '', pd.NA)
        return df.infer_objects(copy=False)
