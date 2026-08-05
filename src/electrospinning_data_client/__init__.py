from typing import Optional, Union, Dict, Any
import pandas as pd

from .client import Client, ElectrospinningDataClient
from .exceptions import (
    ElectrospinningError,
    APIError,
    ValidationError,
    TransportError,
    ParsingError,
    AuthenticationError
)
from .filters import FilterBuilder
from .models import ExperimentRecord, VersionInfo
from .mappers import DataFrameMapper

__version__ = "0.2.0"
__all__ = [
    "Client",
    "ElectrospinningDataClient",
    "FilterBuilder",
    "ExperimentRecord",
    "VersionInfo",
    "DataFrameMapper",
    "ElectrospinningError",
    "APIError",
    "ValidationError",
    "TransportError",
    "ParsingError",
    "AuthenticationError",
    "load_latest_dataset",
    "load_versioned_dataset"
]

def load_latest_dataset(
    filters: Optional[Union[Dict[str, Any], FilterBuilder]] = None
) -> pd.DataFrame:
    """
    Convenience function to load the latest dataset as a pandas DataFrame.
    """
    client = ElectrospinningDataClient()
    try:
        return client.download_latest(filters=filters)
    finally:
        client.close()

def load_versioned_dataset(
    version: str, 
    filters: Optional[Union[Dict[str, Any], FilterBuilder]] = None
) -> pd.DataFrame:
    """
    Convenience function to load a specific dataset version as a pandas DataFrame.
    """
    client = ElectrospinningDataClient()
    try:
        return client.download_version(version, filters=filters)
    finally:
        client.close()
