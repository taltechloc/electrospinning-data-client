import unittest
import pandas as pd
import json
from electrospinning_data_client.client import ElectrospinningDataClient
from electrospinning_data_client.models import ExperimentRecord

class TestExcelParity(unittest.TestCase):
    def setUp(self):
        self.client = ElectrospinningDataClient()

    def test_excel_flattening(self):
        # Create a record that mimics the API's nested structure
        data = {
            "recordId": 123,
            "researchMetadata": {"doi": "10.1000/test"},
            "polymerProperty": {
                "polymerComponents": [
                    {"polymerName": "PAN", "concentration": 10.5}
                ]
            },
            "solutionProperty": {
                "concentration": 12.0,
                "concentrationUnit": "wt%",
                "viscosity": 500,
                "viscosityUnit": "mPa.s"
            },
            "processParameter": {
                "voltage": 25.0,
                "voltageUnit": "kV",
                "flowRate": 0.5,
                "flowRateUnit": "mL/h",
                "tipCollectorDistance": 15.0,
                "tipCollectorDistanceUnit": "cm"
            },
            "fiberProperty": {
                "isFormationStable": "stable",
                "fiberDiameter": 100.0,
                "fiberDiameterUnit": "nm"
            }
        }
        
        record = ExperimentRecord.from_dict(data)
        df = self.client._to_dataframe([record])
        
        # Check IDs and DOI
        self.assertEqual(df.loc[0, 'experiment_id'], 123)
        self.assertEqual(df.loc[0, 'doi'], "10.1000/test")
        
        # Check Polymer/Solvent joins
        self.assertEqual(df.loc[0, 'polymer(s)'], "PAN")
        self.assertEqual(df.loc[0, 'is_polymer_blend'], False)
        
        # Check Solution properties (primary concentration)
        self.assertEqual(df.loc[0, 'solution_concentration'], 12.0)
        self.assertEqual(df.loc[0, 'solution_concentration_unit'], "wt%")
        
        # Check Process parameters
        self.assertEqual(df.loc[0, 'voltage'], 25.0)
        self.assertEqual(df.loc[0, 'voltage_unit'], "kV")
        self.assertEqual(df.loc[0, 'tip_collector_distance'], 15.0)
        self.assertEqual(df.loc[0, 'tip_collector_distance_unit'], "cm")
        
        # Check Types
        self.assertTrue(pd.api.types.is_numeric_dtype(df['solution_concentration']))
        self.assertTrue(pd.api.types.is_numeric_dtype(df['voltage']))

    def test_json_components(self):
        data = {
            "recordId": 1,
            "polymerProperty": {"polymerComponents": [{"polymerName": "PAN"}]}
        }
        record = ExperimentRecord.from_dict(data)
        df = self.client._to_dataframe([record])
        
        # The component field should be a JSON string
        components = json.loads(df.loc[0, 'polymer_components'])
        self.assertEqual(components[0]['name'], "PAN")

    def tearDown(self):
        self.client.close()

if __name__ == '__main__':
    unittest.main()
