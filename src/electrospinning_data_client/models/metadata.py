from dataclasses import dataclass
from typing import Optional, Dict, Any
from .base import validate_required

@dataclass
class ResearchMetadata:
    """Metadata regarding the research publication and device used."""
    doi: Optional[str] = None
    publication_title: Optional[str] = None
    custom_device: Optional[bool] = None
    device_manufacturer: Optional[str] = None
    device_model: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchMetadata":
        return cls(
            doi=data.get("doi"),
            publication_title=data.get("publicationTitle"),
            custom_device=data.get("customDevice"),
            device_manufacturer=data.get("deviceManufacturer"),
            device_model=data.get("deviceModel")
        )
