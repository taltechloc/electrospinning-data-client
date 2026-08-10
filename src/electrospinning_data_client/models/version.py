from dataclasses import dataclass
from typing import Dict, Any, Optional
from .base import to_int, validate_required

@dataclass
class VersionInfo:
    """Represents metadata for a dataset version snapshot."""
    version_identifier: str
    record_count: int
    created_at: str
    doi: Optional[str] = None
    license: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VersionInfo":
        validate_required(data, ["versionIdentifier"])

        return cls(
            version_identifier=str(data.get("versionIdentifier")),
            record_count=to_int(data.get("recordCount")) or 0,
            created_at=str(data.get("createdAt", "")),
            doi=data.get("doi"),
            license=data.get("license")
        )
