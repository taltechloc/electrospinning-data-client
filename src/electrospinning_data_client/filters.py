import json
from typing import Dict, Any, Optional


class FilterBuilder:
    """
    Fluent API for building dataset filters for the Electrospinning Hub API.
    
    Example:
        FilterBuilder().polymer("PAN").voltage(min_val=20, max_val=30).build()
    """
    
    def __init__(self):
        self._filters: Dict[str, Any] = {}

    def polymer(self, value: str) -> "FilterBuilder":
        """Filter by polymer name (case-insensitive contains)."""
        self._filters["polymer"] = value
        return self

    def solvent(self, value: str) -> "FilterBuilder":
        """Filter by solvent name (case-insensitive contains)."""
        self._filters["solvent"] = value
        return self

    def morphology(self, value: str) -> "FilterBuilder":
        """Filter by morphology (e.g., 'Nanofiber')."""
        self._filters["morphology"] = value
        return self

    def voltage(self, min_val: Optional[float] = None, max_val: Optional[float] = None) -> "FilterBuilder":
        """Filter by voltage range (kV)."""
        if min_val is not None:
            self._filters["voltageMin"] = min_val
        if max_val is not None:
            self._filters["voltageMax"] = max_val
        return self

    def flow_rate(self, min_val: Optional[float] = None, max_val: Optional[float] = None) -> "FilterBuilder":
        """Filter by flow rate range (mL/h)."""
        if min_val is not None:
            self._filters["flowRateMin"] = min_val
        if max_val is not None:
            self._filters["flowRateMax"] = max_val
        return self

    def concentration(self, min_val: Optional[float] = None, max_val: Optional[float] = None) -> "FilterBuilder":
        """Filter by concentration range (wt%)."""
        if min_val is not None:
            self._filters["concentrationMin"] = min_val
        if max_val is not None:
            self._filters["concentrationMax"] = max_val
        return self

    def custom(self, key: str, value: Any) -> "FilterBuilder":
        """Add a custom filter key and value directly."""
        self._filters[key] = value
        return self

    def build(self) -> Dict[str, Any]:
        """Return the constructed filter dictionary."""
        return self._filters.copy()

    def __str__(self) -> str:
        """Return JSON string representation of the filters."""
        return json.dumps(self.build())
