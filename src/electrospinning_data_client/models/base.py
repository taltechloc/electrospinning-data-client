from typing import Any, Optional, Dict, List
from ..exceptions import ValidationError

def to_float(value: Any) -> Optional[float]:
    """Safely convert value to float, handles strings and None."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def to_int(value: Any) -> Optional[int]:
    """Safely convert value to int."""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def to_list(value: Any) -> List[Any]:
    """Ensure value is a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

def validate_required(data: Dict[str, Any], fields: List[str]):
    """Validate that required fields are present in data."""
    for field in fields:
        if field not in data or data[field] is None:
            raise ValidationError(f"Missing required field: {field}")
