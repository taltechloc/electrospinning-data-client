from typing import Any, Dict, Optional

from ..exceptions import AuthenticationError
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
        return {"Authorization": f"Bearer {self._api_token}"}

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
