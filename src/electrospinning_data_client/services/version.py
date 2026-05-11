from typing import List
from ..transport import Transport
from ..models import VersionInfo

class VersionService:
    """Service for interacting with dataset versions."""
    
    def __init__(self, transport: Transport, base_url: str):
        self._transport = transport
        self._base_url = base_url.rstrip("/")

    def list_versions(self) -> List[VersionInfo]:
        """Retrieve a list of all available dataset version snapshots."""
        url = f"{self._base_url}/versions"
        response = self._transport.request("GET", url)
        data = response.json()
        return [VersionInfo.from_dict(v) for v in data]
