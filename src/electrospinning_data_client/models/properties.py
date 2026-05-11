from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from .base import to_float, to_list

@dataclass
class SolutionProperty:
    """Chemical and physical properties of the electrospinning solution."""
    concentration: Optional[float] = None
    concentration_unit: Optional[str] = None
    viscosity: Optional[float] = None
    viscosity_unit: Optional[str] = None
    surface_tension: Optional[float] = None
    surface_tension_unit: Optional[str] = None
    conductivity: Optional[float] = None
    conductivity_unit: Optional[str] = None
    evaporation_rate: Optional[float] = None
    evaporation_rate_unit: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SolutionProperty":
        return cls(
            concentration=to_float(data.get("concentration")),
            concentration_unit=data.get("concentrationUnit"),
            viscosity=to_float(data.get("viscosity") or data.get("solutionViscosity")),
            viscosity_unit=data.get("viscosityUnit"),
            surface_tension=to_float(data.get("surfaceTension")),
            surface_tension_unit=data.get("surfaceTensionUnit"),
            conductivity=to_float(data.get("conductivity") or data.get("solutionConductivity")),
            conductivity_unit=data.get("conductivityUnit"),
            evaporation_rate=to_float(data.get("evaporationRate")),
            evaporation_rate_unit=data.get("evaporationRateUnit")
        )

@dataclass
class NeedleProperty:
    """Specific parameters of the spinning needle/nozzle."""
    needle_type: Optional[str] = None
    needle_definition: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NeedleProperty":
        return cls(
            needle_type=data.get("needleType"),
            needle_definition=data.get("needleDefinition")
        )

@dataclass
class CollectorProperty:
    """Specific parameters of the collection system."""
    collector_type: Optional[str] = None
    collector_definition: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CollectorProperty":
        return cls(
            collector_type=data.get("collectorType"),
            collector_definition=data.get("collectorDefinition")
        )

@dataclass
class FiberProperty:
    """Physical and morphological properties of the resulting fibers."""
    is_formation_stable: Optional[str] = None
    fiber_morphology: List[Dict[str, Any]] = field(default_factory=list)
    fiber_diameter: Optional[float] = None
    fiber_diameter_unit: Optional[str] = None
    fiber_diameter_variation: Optional[float] = None
    fiber_diameter_variation_unit: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FiberProperty":
        return cls(
            is_formation_stable=data.get("isFormationStable"),
            fiber_morphology=to_list(data.get("fiberMorphology")),
            fiber_diameter=to_float(data.get("fiberDiameter")),
            fiber_diameter_unit=data.get("fiberDiameterUnit"),
            fiber_diameter_variation=to_float(data.get("fiberDiameterVariation")),
            fiber_diameter_variation_unit=data.get("fiberDiameterVariationUnit")
        )

@dataclass
class MechanicalProperty:
    """Mechanical strength and behavior of the fiber mat/scaffold."""
    tensile_strength: Optional[float] = None
    tensile_strength_unit: Optional[str] = None
    modulus: Optional[float] = None
    modulus_unit: Optional[str] = None
    elongation_at_break: Optional[float] = None
    elongation_at_break_unit: Optional[str] = None
    fracture_behaviour: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MechanicalProperty":
        return cls(
            tensile_strength=to_float(data.get("tensile_strength") or data.get("tensileStrength")),
            tensile_strength_unit=data.get("tensile_strength_unit") or data.get("tensileStrengthUnit"),
            modulus=to_float(data.get("modulus")),
            modulus_unit=data.get("modulus_unit"),
            elongation_at_break=to_float(data.get("elongation_at_break") or data.get("elongationAtBreak")),
            elongation_at_break_unit=data.get("elongation_at_break_unit") or data.get("elongationAtBreakUnit"),
            fracture_behaviour=data.get("fracture_behaviour") or data.get("fractureBehaviour")
        )

@dataclass
class FunctionalProperty:
    """Biological or chemical functional properties of the scaffold."""
    surface_area: Optional[float] = None
    surface_area_unit: Optional[str] = None
    porosity: Optional[float] = None
    porosity_unit: Optional[str] = None
    permeability: Optional[float] = None
    permeability_unit: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FunctionalProperty":
        return cls(
            surface_area=to_float(data.get("surface_area") or data.get("surfaceArea")),
            surface_area_unit=data.get("surface_area_unit") or data.get("surfaceAreaUnit"),
            porosity=to_float(data.get("porosity")),
            porosity_unit=data.get("porosity_unit"),
            permeability=to_float(data.get("permeability")),
            permeability_unit=data.get("permeability_unit")
        )
