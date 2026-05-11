from dataclasses import dataclass
from typing import Dict, Any
from ..exceptions import ValidationError
from .base import validate_required

@dataclass
class PolymerComponent:
    """Represents a polymer component in a solution."""
    name: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PolymerComponent":
        name = data.get("polymerName") or data.get("name")
        if not name:
            raise ValidationError("Polymer name is required")
        return cls(name=name)

@dataclass
class SolventComponent:
    """Represents a solvent component in a solution."""
    name: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SolventComponent":
        name = data.get("solventName") or data.get("name")
        if not name:
            raise ValidationError("Solvent name is required")
        return cls(name=name)
