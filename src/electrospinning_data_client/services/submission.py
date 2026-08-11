from typing import Any, Dict, List, Optional

from .. import environments
from ..exceptions import AuthenticationError, EnvironmentMismatchError
from ..transport import Transport


class SubmissionService:
    """
    Service for authenticated write operations (submitting/updating experiment
    data, and checking submission status). Unlike dataset reads, these
    endpoints require a personal access token created from the contributor's
    profile settings on the website.
    """

    def __init__(self, transport: Transport, root_url: str, api_token: Optional[str] = None):
        self._transport = transport
        self._root_url = root_url.rstrip("/")
        self._api_token = api_token

    def _auth_headers(self) -> Dict[str, str]:
        if not self._api_token:
            raise AuthenticationError(
                "An API token is required for write operations. Create one from your "
                "profile settings on the website, then pass it as `api_token=` when "
                "constructing ElectrospinningDataClient."
            )
        self._check_environment_match()
        return {"Authorization": f"Bearer {self._api_token}"}

    def _check_environment_match(self) -> None:
        """
        Client-side convenience check: catch an obvious sandbox/production
        mismatch before making a network call at all. Silently skipped
        whenever either side (token prefix or URL host) isn't one of the two
        recognized shapes -- e.g. a custom base_url pointing at localhost --
        since that's not necessarily a mistake. The server performs the real,
        authoritative check regardless of what happens here.
        """
        token_env = environments.infer_environment_from_token(self._api_token)
        url_env = environments.infer_environment_from_url(self._root_url)
        if token_env is not None and url_env is not None and token_env != url_env:
            raise EnvironmentMismatchError(
                f"This token looks like a {token_env} token (by its prefix), but the "
                f"configured API endpoint ({self._root_url}) looks like {url_env}. "
                "Use a token and endpoint from the same environment -- see the "
                "`environment=` parameter on Client for the easiest way to keep them "
                "in sync."
            )

    def submit(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST a new experiment submission. Returns the parsed JSON result."""
        headers = self._auth_headers()
        response = self._transport.request(
            "POST", f"{self._root_url}/data/submit", json=payload, headers=headers
        )
        return response.json()

    def update(self, experiment_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """PUT an update to an existing experiment. Returns the parsed JSON result."""
        headers = self._auth_headers()
        response = self._transport.request(
            "PUT", f"{self._root_url}/data/update/{experiment_id}", json=payload, headers=headers
        )
        return response.json()

    def get_submission(self, submission_id: int) -> Dict[str, Any]:
        """GET the current state (including per-record status) of a submission."""
        headers = self._auth_headers()
        response = self._transport.request(
            "GET", f"{self._root_url}/data/submission/{submission_id}", headers=headers
        )
        return response.json()

    def list_my_records(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        GET the caller's own experiment records, optionally filtered to a single
        status (e.g. "NEEDS_UPDATE"). Omit `status` to get every record
        regardless of status.
        """
        headers = self._auth_headers()
        params = {"status": status} if status else None
        response = self._transport.request(
            "GET", f"{self._root_url}/data/my-records", headers=headers, params=params
        )
        return response.json()

    def list_my_record_ids(self, status: Optional[str] = None) -> List[int]:
        """Same filtering as `list_my_records`, but returns only record ids."""
        headers = self._auth_headers()
        params = {"status": status} if status else None
        response = self._transport.request(
            "GET", f"{self._root_url}/data/my-records/ids", headers=headers, params=params
        )
        return response.json()
