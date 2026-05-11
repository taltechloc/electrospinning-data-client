import unittest
from electrospinning_data_client.models import ExperimentRecord, VersionInfo
from electrospinning_data_client.exceptions import ValidationError

class TestModels(unittest.TestCase):
    def test_record_from_dict_success(self):
        data = {
            "recordId": "1",  # Test string ID coercion
            "researchMetadata": {"doi": "10.1234/test"},
            "polymerProperty": {"polymerComponents": [{"polymerName": "PAN"}]},
            "solutionProperty": {"concentration": "10.5", "concentrationUnit": "wt%"},
            "fiberProperty": {"isFormationStable": "stable"}
        }
        record = ExperimentRecord.from_dict(data)
        
        self.assertEqual(record.record_id, 1)
        self.assertEqual(record.research_metadata.doi, "10.1234/test")
        self.assertEqual(record.polymer_components[0].name, "PAN")
        self.assertEqual(record.solution_property.concentration, 10.5)
        self.assertEqual(record.fiber_property.is_formation_stable, "stable")

    def test_record_missing_id_raises_error(self):
        data = {"researchMetadata": {"doi": "10.1234/test"}}
        with self.assertRaises(ValidationError) as cm:
            ExperimentRecord.from_dict(data)
        self.assertIn("recordId", str(cm.exception))

    def test_polymer_missing_name_raises_error(self):
        data = {
            "recordId": 1,
            "polymerProperty": {"polymerComponents": [{}]}
        }
        with self.assertRaises(ValidationError):
            ExperimentRecord.from_dict(data)

    def test_invalid_float_coercion(self):
        data = {
            "recordId": 1,
            "solutionProperty": {"concentration": "not-a-number"}
        }
        record = ExperimentRecord.from_dict(data)
        self.assertIsNone(record.solution_property.concentration)

    def test_version_info_validation(self):
        with self.assertRaises(ValidationError):
            VersionInfo.from_dict({"recordCount": 10})

    def test_version_info_success(self):
        data = {
            "versionIdentifier": "v1.0.0",
            "recordCount": "100"
        }
        v = VersionInfo.from_dict(data)
        self.assertEqual(v.version_identifier, "v1.0.0")
        self.assertEqual(v.record_count, 100)

if __name__ == '__main__':
    unittest.main()
