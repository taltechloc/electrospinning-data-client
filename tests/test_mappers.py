import unittest
from electrospinning_data_client.models import (
    ExperimentRecord, ResearchMetadata, PolymerComponent, SolutionProperty
)
from electrospinning_data_client.mappers import DataFrameMapper

class TestDataFrameMapper(unittest.TestCase):
    def setUp(self):
        self.sample_data = {
            "recordId": 123,
            "researchMetadata": {
                "doi": "10.1234/test",
                "publicationTitle": "Test Publication"
            },
            "polymerProperty": {
                "polymerComponents": [{"polymerName": "PAN"}]
            },
            "solutionProperty": {
                "concentration": 10.5,
                "concentrationUnit": "wt%"
            },
            "processParameter": {
                "voltage": 20.0,
                "voltageUnit": "kV"
            },
            "fiberProperty": {
                "fiberDiameter": 250.0,
                "fiberDiameterUnit": "nm"
            }
        }
        self.record = ExperimentRecord.from_dict(self.sample_data)

    def test_to_row_basic(self):
        row = DataFrameMapper.to_row(self.record)
        self.assertEqual(row["experiment_id"], 123)
        self.assertEqual(row["doi"], "10.1234/test")
        self.assertEqual(row["polymer(s)"], "PAN")
        self.assertEqual(row["voltage"], 20.0)
        self.assertEqual(row["fiber_diameter"], 250.0)

    def test_polymer_blend(self):
        self.sample_data["polymerProperty"]["polymerComponents"].append(
            {"polymerName": "PVP"}
        )
        record = ExperimentRecord.from_dict(self.sample_data)
        row = DataFrameMapper.to_row(record)
        self.assertTrue(row["is_polymer_blend"])
        self.assertEqual(row["polymer(s)"], "PAN-PVP")

    def test_map_records(self):
        records = [self.record, self.record]
        rows = DataFrameMapper.map_records(records)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["experiment_id"], 123)

if __name__ == "__main__":
    unittest.main()
