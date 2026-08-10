from typing import List, Dict, Any, Optional, Union
import json
from ..transport import Transport
from ..models import ExperimentRecord
from ..filters import FilterBuilder


class DatasetService:
    """Service for interacting with dataset records."""
    
    def __init__(self, transport: Transport, base_url: str):
        self._transport = transport
        self._base_url = base_url.rstrip("/")

    def get_records(
        self,
        version: str = "latest",
        filters: Optional[Union[Dict[str, Any], FilterBuilder]] = None
    ) -> List[ExperimentRecord]:
        """Fetch full dataset records as domain models."""
        params = {"format": "json"}
        if filters:
            params["filter"] = (
                str(filters) if isinstance(filters, FilterBuilder)
                else json.dumps(filters)
            )

        url, params = self._export_url_and_params(version, params)

        response = self._transport.request("GET", url, params=params)
        data = response.json()
        
        if not isinstance(data, list):
            # Handle cases where the API might return a wrapped object
            if "data" in data and isinstance(data["data"], list):
                data = data["data"]
            else:
                return []
                
        return [ExperimentRecord.from_dict(r) for r in data]

    def export(
        self,
        output_path: str,
        export_format: str = "xlsx",
        version: str = "latest",
        filters: Optional[Union[Dict[str, Any], FilterBuilder]] = None
    ):
        """Export dataset to a local file."""
        params = {"format": export_format}
        if filters:
            params["filter"] = (
                str(filters) if isinstance(filters, FilterBuilder)
                else json.dumps(filters)
            )

        url, params = self._export_url_and_params(version, params)

        response = self._transport.request("GET", url, params=params)
        with open(output_path, "wb") as f:
            f.write(response.content)

    def _export_url_and_params(self, version: str, params: Dict[str, Any]):
        """Route a versioned export request.

        Plain identifiers (e.g. "v1.0.0") use the /{version}/export path
        shortcut. DOIs contain '/', which that path segment can't carry, so
        they're passed via the generic /export endpoint's `version` query
        param instead.
        """
        if version == "latest":
            return f"{self._base_url}/export", params
        if "/" in version:
            return f"{self._base_url}/export", {**params, "version": version}
        return f"{self._base_url}/{version}/export", params

    def load_paginated(
        self,
        skip: int = 0,
        limit: int = 100,
        version: str = "latest",
        filters: Optional[Union[Dict[str, Any], FilterBuilder]] = None
    ) -> Dict[str, Any]:
        """Fetch a paginated slice of raw records."""
        params = {"skip": skip, "limit": limit}
        if filters:
            params["filter"] = (
                str(filters) if isinstance(filters, FilterBuilder)
                else json.dumps(filters)
            )

        endpoint = "" if version == "latest" else f"/{version}"
        url = f"{self._base_url}{endpoint}"

        return self._transport.request("GET", url, params=params).json()
