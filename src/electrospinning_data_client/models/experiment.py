from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from .base import to_int, validate_required
from .metadata import ResearchMetadata
from .components import PolymerComponent, SolventComponent
from .properties import (
    SolutionProperty, NeedleProperty, CollectorProperty, 
    FiberProperty, MechanicalProperty, FunctionalProperty
)
from .parameters import ProcessParameter, AmbientParameter

@dataclass
class ExperimentRecord:
    """Represents a single experiment record in the dataset."""
    record_id: int
    research_metadata: ResearchMetadata = field(default_factory=ResearchMetadata)
    polymer_components: List[PolymerComponent] = field(default_factory=list)
    solvent_components: List[SolventComponent] = field(default_factory=list)
    solution_property: SolutionProperty = field(default_factory=SolutionProperty)
    needle_property: NeedleProperty = field(default_factory=NeedleProperty)
    collector_property: CollectorProperty = field(default_factory=CollectorProperty)
    process_parameter: ProcessParameter = field(default_factory=ProcessParameter)
    ambient_parameter: AmbientParameter = field(default_factory=AmbientParameter)
    fiber_property: FiberProperty = field(default_factory=FiberProperty)
    mechanical_property: MechanicalProperty = field(default_factory=MechanicalProperty)
    functional_property: FunctionalProperty = field(default_factory=FunctionalProperty)
    
    # Raw data for backward compatibility or debugging
    raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentRecord":
        """
        Create a record from a dictionary, mapping API camelCase to snake_case.
        Includes defensive validation for required identifiers.
        """
        record_id = to_int(data.get("recordId") or data.get("experimentId"))
        if record_id is None:
            validate_required(data, ["recordId"])

        poly_prop = data.get("polymerProperty", {}) or {}
        poly_components = [
            PolymerComponent.from_dict(p)
            for p in poly_prop.get("polymerComponents", [])
            if p is not None
        ]
        
        solv_prop = data.get("solventProperty", {}) or {}
        solv_components = [
            SolventComponent.from_dict(s)
            for s in solv_prop.get("solventComponents", [])
            if s is not None
        ]

        return cls(
            record_id=record_id,
            research_metadata=ResearchMetadata.from_dict(data.get("researchMetadata", {}) or {}),
            polymer_components=poly_components,
            solvent_components=solv_components,
            solution_property=SolutionProperty.from_dict(data.get("solutionProperty", {}) or {}),
            needle_property=NeedleProperty.from_dict(data.get("needleProperty", {}) or {}),
            collector_property=CollectorProperty.from_dict(data.get("collectorProperty", {}) or {}),
            process_parameter=ProcessParameter.from_dict(data.get("processParameter", {}) or {}),
            ambient_parameter=AmbientParameter.from_dict(data.get("ambientParameter", {}) or {}),
            fiber_property=FiberProperty.from_dict(data.get("fiberProperty", {}) or {}),
            mechanical_property=MechanicalProperty.from_dict(data.get("mechanicalProperty", {}) or {}),
            functional_property=FunctionalProperty.from_dict(data.get("functionalProperty", {}) or {}),
            raw_data=data
        )
