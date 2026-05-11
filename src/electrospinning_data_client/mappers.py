import json
from dataclasses import asdict
from typing import Dict, Any, List, Optional
from .models import ExperimentRecord

class DataFrameMapper:
    """
    Handles the transformation of domain models into flattened
    dictionary structures suitable for pandas DataFrame conversion.
    """

    @staticmethod
    def to_row(record: ExperimentRecord) -> Dict[str, Any]:
        """Flattens an ExperimentRecord into a single-level dictionary."""
        row = {}
        
        # 1. Core Identifiers
        row["doi"] = record.research_metadata.doi
        row["experiment_id"] = record.record_id

        # 2. Polymer Blend logic
        row["is_polymer_blend"] = len(record.polymer_components) > 1
        row["polymer(s)"] = "-".join([p.name for p in record.polymer_components])
        row["polymer_components"] = json.dumps(
            [asdict(p) for p in record.polymer_components]
        ) if record.polymer_components else None

        # 3. Solvent Blend logic
        row["is_solvent_blend"] = len(record.solvent_components) > 1
        row["solvent(s)"] = "-".join([s.name for s in record.solvent_components])
        row["solvent_components"] = json.dumps(
            [asdict(s) for s in record.solvent_components]
        ) if record.solvent_components else None

        # 4. Solution Properties
        sp = record.solution_property
        row["solution_concentration"] = sp.concentration
        row["solution_concentration_unit"] = sp.concentration_unit
        row["solution_viscosity"] = sp.viscosity
        row["solution_viscosity_unit"] = sp.viscosity_unit
        row["solution_surface_tension"] = sp.surface_tension
        row["solution_surface_tension_unit"] = sp.surface_tension_unit
        row["solution_conductivity"] = sp.conductivity
        row["solution_conductivity_unit"] = sp.conductivity_unit
        row["solution_evaporation_rate"] = sp.evaporation_rate
        row["solution_evaporation_rate_unit"] = sp.evaporation_rate_unit

        # 5. Needle & Collector
        np = record.needle_property
        row["needle_type"] = np.needle_type
        row["needle_definition"] = json.dumps(
            np.needle_definition
        ) if np.needle_definition else None
        
        cp = record.collector_property
        row["collector_type"] = cp.collector_type
        row["collector_definition"] = json.dumps(
            cp.collector_definition
        ) if cp.collector_definition else None

        # 6. Process Parameters
        pp = record.process_parameter
        row["voltage"] = pp.voltage
        row["voltage_unit"] = pp.voltage_unit
        row["flow_rate"] = pp.flow_rate
        row["flow_rate_unit"] = pp.flow_rate_unit
        row["tip_collector_distance"] = pp.tip_collector_distance
        row["tip_collector_distance_unit"] = pp.tip_collector_distance_unit
        row["spinning_duration"] = pp.spinning_duration
        row["spinning_duration_unit"] = pp.spinning_duration_unit

        # 7. Ambient Parameters
        ap = record.ambient_parameter
        row["temperature"] = ap.temperature
        row["temperature_unit"] = ap.temperature_unit
        row["humidity"] = ap.humidity
        row["humidity_unit"] = ap.humidity_unit

        # 8. Fiber Properties
        fp = record.fiber_property
        row["was_formation_stable"] = fp.is_formation_stable
        row["process_instability"] = json.dumps(
            pp.instability
        ) if pp.instability else None
        row["fiber_diameter"] = fp.fiber_diameter
        row["fiber_diameter_unit"] = fp.fiber_diameter_unit
        row["fiber_diameter_variation"] = fp.fiber_diameter_variation
        row["fiber_diameter_variation_unit"] = (
            fp.fiber_diameter_variation_unit
        )
        row["morphology"] = json.dumps(
            fp.fiber_morphology
        ) if fp.fiber_morphology else None

        # 9. Extra Metadata
        rm = record.research_metadata
        row["publication_title"] = rm.publication_title
        row["is_custom_device"] = rm.custom_device
        row["device_manufacturer"] = rm.device_manufacturer
        row["device_model"] = rm.device_model

        # 10. Mechanical Properties
        mp = record.mechanical_property
        row["tensile_strength"] = mp.tensile_strength
        row["tensile_strength_unit"] = mp.tensile_strength_unit
        row["modulus"] = mp.modulus
        row["modulus_unit"] = mp.modulus_unit
        row["elongation_at_break"] = mp.elongation_at_break
        row["elongation_at_break_unit"] = mp.elongation_at_break_unit
        row["fracture_behaviour"] = mp.fracture_behaviour

        # 11. Functional Properties
        funp = record.functional_property
        row["surface_area"] = funp.surface_area
        row["surface_area_unit"] = funp.surface_area_unit
        row["porosity"] = funp.porosity
        row["porosity_unit"] = funp.porosity_unit
        row["permeability"] = funp.permeability
        row["permeability_unit"] = funp.permeability_unit

        return row

    @classmethod
    def map_records(cls, records: List[ExperimentRecord]) -> List[Dict[str, Any]]:
        """Maps a list of ExperimentRecord objects to a list of flattened rows."""
        return [cls.to_row(r) for r in records]
