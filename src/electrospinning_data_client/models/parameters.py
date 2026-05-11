from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from .base import to_float, to_list

@dataclass
class ProcessParameter:
    """Core electrospinning process parameters (voltage, flow rate, etc.)."""
    voltage: Optional[float] = None
    voltage_unit: Optional[str] = None
    flow_rate: Optional[float] = None
    flow_rate_unit: Optional[str] = None
    tip_collector_distance: Optional[float] = None
    tip_collector_distance_unit: Optional[str] = None
    spinning_duration: Optional[float] = None
    spinning_duration_unit: Optional[str] = None
    instability: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessParameter":
        return cls(
            voltage=to_float(data.get("voltage")),
            voltage_unit=data.get("voltageUnit"),
            flow_rate=to_float(data.get("flowRate")),
            flow_rate_unit=data.get("flowRateUnit"),
            tip_collector_distance=to_float(data.get("tipCollectorDistance")),
            tip_collector_distance_unit=data.get("tipCollectorDistanceUnit"),
            spinning_duration=to_float(data.get("spinningDuration")),
            spinning_duration_unit=data.get("spinningDurationUnit"),
            instability=to_list(data.get("instability"))
        )

@dataclass
class AmbientParameter:
    """Environmental conditions during the spinning process."""
    temperature: Optional[float] = None
    temperature_unit: Optional[str] = None
    humidity: Optional[float] = None
    humidity_unit: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AmbientParameter":
        return cls(
            temperature=to_float(data.get("temperature")),
            temperature_unit=data.get("temperatureUnit"),
            humidity=to_float(data.get("humidity")),
            humidity_unit=data.get("humidityUnit")
        )
