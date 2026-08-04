from typing import List, Dict, Any, Optional, Union
from urllib.parse import urlsplit

import pandas as pd

from .filters import FilterBuilder
from .mappers import DataFrameMapper
from .models import ExperimentRecord, VersionInfo
from .services.dataset import DatasetService
from .services.submission import SubmissionService
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
        verify: bool = True,
        api_token: Optional[str] = None,
        api_base_url: Optional[str] = None
    ):
        """
        Initialize the Electrospinning Hub API client.

        Args:
            base_url: The base URL of the public (read) API.
            transport: Custom HTTP transport implementation.
            timeout: Default request timeout in seconds.
            verify: Whether to verify SSL certificates.
            api_token: Personal access token (created from your profile settings on
                the website) used to authenticate write operations such as
                `submit_experiment`. Not required for any read/download method.
            api_base_url: Root URL of the API used for write operations, e.g.
                "https://api.electrospinning-data.org". Defaults to the scheme and
                host of `base_url`, since write endpoints live outside the
                `/public/dataset` read API.
        """
        self.base_url = base_url.rstrip("/")
        self.transport = transport or RequestsTransport(
            timeout=timeout, verify=verify
        )

        if api_base_url:
            self.api_base_url = api_base_url.rstrip("/")
        else:
            parsed = urlsplit(self.base_url)
            self.api_base_url = f"{parsed.scheme}://{parsed.netloc}"

        # Internal services
        self._dataset_service = DatasetService(self.transport, self.base_url)
        self._version_service = VersionService(self.transport, self.base_url)
        self._submission_service = SubmissionService(self.transport, self.api_base_url, api_token)

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

    def submit_experiment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a new experiment record for moderation. Requires `api_token` to
        have been passed when constructing the client - create a token from
        your profile settings on the website first.

        `payload` is a plain dict matching the submission JSON shape used by the
        website's submission form, e.g.:

            {
                "userMetadata": {"name": "...", "email": "...", "consentTerms": True},
                "researchMetadata": {"publicationTitle": "...", "doi": "..."},
                "experimentData": [{"polymerProperty": {...}, "processParameter": {...}, ...}]
            }

        Mandatory scientific fields (currently: polymer info, and any solvent
        component's name) may be omitted - the record is still saved, just with
        status "NEEDS_UPDATE" instead of "PENDING", so you can fill them in later
        via `update_experiment`. This is a normal, successful outcome (no
        exception is raised); inspect the returned `records[i]["status"]` and
        `records[i]["missingFields"]` to see what's still needed.

        Args:
            payload: The submission payload.

        Returns:
            A dict shaped like:

                {
                    "message": "Data submitted successfully",
                    "submissionId": 123,
                    "records": [
                        {"recordId": 45, "status": "PENDING", "missingFields": []},
                        {"recordId": 46, "status": "NEEDS_UPDATE",
                         "missingFields": ["polymerProperty.polymerComponents[].polymerName"]}
                    ]
                }

        Raises:
            AuthenticationError: If no `api_token` was configured.
            APIError: If the server rejects the token (missing/invalid/expired/revoked),
                or a *provided* reference doesn't resolve (e.g. an unknown polymer name -
                that's a data-quality error, not incompleteness, and always blocks).
        """
        return self._submission_service.submit(payload)

    def update_experiment(self, experiment_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing experiment record you previously submitted - typically
        used to fill in the fields flagged by a prior NEEDS_UPDATE response.
        Requires `api_token` to have been passed when constructing the client.
        See `submit_experiment` for the payload shape.

        If the update now supplies all mandatory fields, the record's status
        flips from "NEEDS_UPDATE" back to "PENDING" and re-enters the
        moderation queue automatically.

        Args:
            experiment_id: The id of the experiment record to update.
            payload: The updated submission payload.

        Returns:
            A dict shaped like:
                {"recordId": 45, "status": "PENDING", "missingFields": [], "message": "..."}

        Raises:
            AuthenticationError: If no `api_token` was configured.
            APIError: If the server rejects the token or the request (e.g. you
                don't own the experiment).
        """
        return self._submission_service.update(experiment_id, payload)

    def get_submission_status(self, submission_id: int) -> Dict[str, Any]:
        """
        Retrieve the current state of a submission you own, including the
        status ("PENDING", "APPROVED", "REJECTED", "NEEDS_UPDATE", or "MIXED"
        if its records have different statuses) of each experiment record in it.
        Requires `api_token`.

        Args:
            submission_id: The id returned as `submissionId` by `submit_experiment`.

        Returns:
            The full submission, e.g. `{"submissionId": 123, "status": "NEEDS_UPDATE",
            "experimentData": [...]}` - each item in `experimentData` has its own `status`.

        Raises:
            AuthenticationError: If no `api_token` was configured.
            APIError: If the submission doesn't exist or isn't yours.
        """
        return self._submission_service.get_submission(submission_id)

    def list_my_records(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List your own submitted experiment records (flat, not grouped by
        submission), optionally filtered to a single status. This gives you the
        freedom to query your data per status or all together:

            client.list_my_records()                     # every record, any status
            client.list_my_records(status="NEEDS_UPDATE")  # only incomplete records
            client.list_my_records(status="PENDING")       # only records awaiting review

        Requires `api_token`.

        Args:
            status: One of "PENDING", "APPROVED", "REJECTED", "NEEDS_UPDATE", or
                None (default) for every status combined.

        Returns:
            A list of full experiment record dicts (same shape as items in
            `submit_experiment`'s `experimentData`), each with its own `status`.

        Raises:
            AuthenticationError: If no `api_token` was configured.
            APIError: If the server rejects the token.
        """
        return self._submission_service.list_my_records(status)

    def list_my_record_ids(self, status: Optional[str] = None) -> List[int]:
        """
        Same filtering as `list_my_records`, but returns only record ids -
        useful for cheaply checking what needs attention (e.g. how many records
        are NEEDS_UPDATE) before fetching full data.

        Requires `api_token`.

        Args:
            status: One of "PENDING", "APPROVED", "REJECTED", "NEEDS_UPDATE", or
                None (default) for every status combined.

        Returns:
            A list of record ids (ints).

        Raises:
            AuthenticationError: If no `api_token` was configured.
            APIError: If the server rejects the token.
        """
        return self._submission_service.list_my_record_ids(status)

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
