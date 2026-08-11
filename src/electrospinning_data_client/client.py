from typing import List, Dict, Any, Optional, Union
from urllib.parse import urlsplit

import pandas as pd

from . import environments
from .filters import FilterBuilder
from .mappers import DataFrameMapper
from .models import ExperimentRecord, VersionInfo
from .services.dataset import DatasetService
from .services.submission import SubmissionService
from .services.version import VersionService
from .transport import Transport, RequestsTransport


class Client:
    """
    Main client for interacting with the Electrospinning Data Public API.
    Provides methods for downloading datasets, listing versions, submitting
    and updating experiment records, and querying your own submissions.

    This is the primary entry point for the package:

        from electrospinning_data_client import Client

        client = Client(token="esd_pat_your_token_here")
        df = client.download()
        client.submit(payload)

    Two environments are deployed: Sandbox (development/integration testing -
    isolated, disposable data) and Production (real submissions). For write
    integration work, create a sandbox token from your profile settings on
    the website and pass `environment="sandbox"` while you build and test,
    then switch to a production token and `environment="production"` once
    you're ready to submit real records:

        client = Client(token="esd_sandbox_...", environment="sandbox")
        client.submit(payload)  # goes to sandbox-api.electrospinning-data.org

        client = Client(token="esd_pat_...", environment="production")
        client.submit(payload)  # goes to api.electrospinning-data.org, for real

    `environment=` only sets defaults for `base_url`/`api_base_url` - an
    explicit `base_url=`/`api_base_url=` always wins if given, so existing
    code that already passes a custom URL is never silently redirected.
    Omitting both `environment` and `base_url` keeps today's default (the
    production read API), so existing read-only usage is unaffected.

    Every method below has a short, Pythonic alias (`submit`, `update`,
    `status`, `download`, `search`, `records`, `record_ids`, `versions`) as
    well as its original, more descriptive name (`submit_experiment`,
    `update_experiment`, `get_submission_status`, `download_latest` /
    `download_version`, `list_my_records`, `list_my_record_ids`,
    `get_versions`) - both call exactly the same code, so pick whichever
    reads best at the call site. `ElectrospinningDataClient` is kept as an
    alias of this exact class for existing code.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        transport: Optional[Transport] = None,
        timeout: int = 60,
        verify: bool = True,
        token: Optional[str] = None,
        api_token: Optional[str] = None,
        api_base_url: Optional[str] = None,
        environment: Optional[str] = None,
    ):
        """
        Initialize the Electrospinning Data API client.

        Args:
            base_url: The base URL of the public (read) API. Takes precedence
                over `environment` if both are given. Defaults to the
                production read API if neither `base_url` nor `environment`
                is given, matching this client's historical default.
            transport: Custom HTTP transport implementation.
            timeout: Default request timeout in seconds.
            verify: Whether to verify SSL certificates.
            token: Personal access token (created from your profile settings on
                the website) used to authenticate write operations such as
                `submit`/`update`. Not required for any read/download method.
                This is the preferred name; `api_token` is kept as an alias for
                existing code and is used if `token` is not given.
            api_token: Deprecated alias for `token`, kept for backward
                compatibility. Ignored if `token` is also given.
            api_base_url: Root URL of the API used for write operations, e.g.
                "https://api.electrospinning-data.org". Takes precedence over
                `environment` if both are given. Defaults to the scheme and
                host of `base_url` (or, if `environment` is given and
                `base_url` isn't, that environment's write API root), since
                write endpoints live outside the `/public/dataset` read API.
            environment: `"sandbox"` or `"production"` (case-insensitive).
                Sets the default for `base_url`/`api_base_url` to that
                environment's known URLs - see the class docstring for the
                intended sandbox-first write-integration workflow. Ignored
                for whichever of `base_url`/`api_base_url` is explicitly
                given. `None` (default) preserves this client's historical
                behavior: no environment-based defaulting, and a client-side
                token/URL mismatch check (see `EnvironmentMismatchError`) is
                skipped for the URL side.
        """
        if base_url is not None:
            self.base_url = base_url.rstrip("/")
        elif environment is not None:
            self.base_url, _ = environments.resolve_urls(environment)
        else:
            self.base_url = environments.DEFAULT_BASE_URL

        self.transport = transport or RequestsTransport(
            timeout=timeout, verify=verify
        )

        if api_base_url:
            self.api_base_url = api_base_url.rstrip("/")
        elif environment is not None:
            _, self.api_base_url = environments.resolve_urls(environment)
        else:
            parsed = urlsplit(self.base_url)
            self.api_base_url = f"{parsed.scheme}://{parsed.netloc}"

        self.environment = environment.strip().lower() if environment else None

        resolved_token = token if token is not None else api_token

        # Internal services
        self._dataset_service = DatasetService(self.transport, self.base_url)
        self._version_service = VersionService(self.transport, self.base_url)
        self._submission_service = SubmissionService(
            self.transport, self.api_base_url, resolved_token
        )

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

    # ------------------------------------------------------------------
    # Short, ergonomic aliases
    #
    # Each of these is a thin wrapper around one of the methods above -
    # nothing here changes behavior, they just give the common operations
    # shorter, more Pythonic names for day-to-day use:
    #
    #     client.submit(payload)               == client.submit_experiment(payload)
    #     client.update(id, payload)           == client.update_experiment(id, payload)
    #     client.status(submission_id)         == client.get_submission_status(submission_id)
    #     client.download()                    == client.download_latest()
    #     client.download(version="v1.0.0")    == client.download_version("v1.0.0")
    #     client.search(filters={...})         == client.download_latest(filters={...})
    #     client.records(status=...)           == client.list_my_records(status=...)
    #     client.record_ids(status=...)        == client.list_my_record_ids(status=...)
    #     client.versions()                    == client.get_versions()
    # ------------------------------------------------------------------

    def submit(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a new experiment record for moderation. Short alias for
        `submit_experiment` - see that method for the full docstring
        (payload shape, `NEEDS_UPDATE` behavior, exceptions).

        Example:
            >>> client = Client(token="esd_pat_...")
            >>> result = client.submit({
            ...     "userMetadata": {"name": "Jane Doe", "email": "jane@example.com", "consentTerms": True},
            ...     "experimentData": [{"polymerProperty": {}, "processParameter": {}}],
            ... })
            >>> result["records"][0]["status"]
            'PENDING'
        """
        return self.submit_experiment(record)

    def update(self, id: int, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an experiment record you previously submitted. Short alias
        for `update_experiment` - see that method for the full docstring.

        Example:
            >>> client.update(45, {"experimentData": [{"polymerProperty": {...}}]})
            {'recordId': 45, 'status': 'PENDING', 'missingFields': [], 'message': '...'}
        """
        return self.update_experiment(id, record)

    def status(self, submission_id: int) -> Dict[str, Any]:
        """
        Get the current state of a submission you own. Short alias for
        `get_submission_status` - see that method for the full docstring.

        Example:
            >>> client.status(123)["status"]
            'NEEDS_UPDATE'
        """
        return self.get_submission_status(submission_id)

    def download(
        self,
        version: Optional[str] = None,
        filters: Optional[Union[Dict[str, Any], FilterBuilder]] = None
    ) -> pd.DataFrame:
        """
        Download a dataset snapshot as a pandas DataFrame - the latest one
        by default, or a specific version if `version` is given. Short
        alias combining `download_latest` and `download_version`.

        Args:
            version: Version identifier (e.g. "v1.0.0"), or None (default)
                for the latest snapshot.
            filters: Optional filters (dict or `FilterBuilder`) to apply.

        Returns:
            A pandas DataFrame containing the flattened records.

        Example:
            >>> client.download()                      # latest
            >>> client.download(version="v1.0.0")       # a specific, reproducible snapshot
            >>> client.download(filters={"polymer": "PAN"})
        """
        if version is None or version == "latest":
            return self.download_latest(filters=filters)
        return self.download_version(version, filters=filters)

    def search(
        self,
        filters: Optional[Union[Dict[str, Any], FilterBuilder]] = None,
        version: str = "latest"
    ) -> pd.DataFrame:
        """
        Query the dataset with filters, returned as a pandas DataFrame.
        Equivalent to `download(version=version, filters=filters)` - use
        whichever name reads better when filtering is the point of the call.

        Args:
            filters: Filters to apply (dict or `FilterBuilder`), e.g.
                `{"polymer": "PAN", "voltageMin": 20}`.
            version: Dataset version to search within. Defaults to "latest".

        Returns:
            A pandas DataFrame containing the matching, flattened records.

        Example:
            >>> client.search(filters={"polymer": "PAN"})
            >>> client.search(filters=FilterBuilder().solvent("DMF").build())
        """
        return self.download(version=version, filters=filters)

    def records(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List your own submitted experiment records, optionally filtered to
        one status. Short alias for `list_my_records`.

        Example:
            >>> client.records(status="NEEDS_UPDATE")
        """
        return self.list_my_records(status)

    def record_ids(self, status: Optional[str] = None) -> List[int]:
        """
        List the ids of your own submitted experiment records, optionally
        filtered to one status. Short alias for `list_my_record_ids`.

        Example:
            >>> client.record_ids(status="NEEDS_UPDATE")
        """
        return self.list_my_record_ids(status)

    def versions(self) -> List[VersionInfo]:
        """
        List all available dataset version snapshots. Short alias for
        `get_versions`.

        Example:
            >>> [v.version_identifier for v in client.versions()]
        """
        return self.get_versions()

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


# Backward-compatible alias: `ElectrospinningDataClient` is the exact same
# class object as `Client` (not a subclass or a copy), so existing code -
# including `isinstance(x, ElectrospinningDataClient)` checks - keeps working
# unchanged. `Client` is the name new code should use.
ElectrospinningDataClient = Client
