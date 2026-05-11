import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import json
from electrospinning_data_client import ElectrospinningDataClient, APIError, ValidationError

class TestElectrospinningDataClient(unittest.TestCase):

    def setUp(self):
        self.client = ElectrospinningDataClient(base_url="https://api.example.com")

    @patch('requests.Session.request')
    def test_get_versions(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = [{
            "versionIdentifier": "v1.0.0",
            "recordCount": 100,
            "createdAt": "2024-01-01"
        }]
        mock_request.return_value = mock_response

        versions = self.client.get_versions()
        
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0].version_identifier, "v1.0.0")
        mock_request.assert_called_with("GET", "https://api.example.com/versions", timeout=60, verify=True)

    @patch('requests.Session.request')
    def test_download_latest(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        # Mock data with nested structure
        mock_response.json.return_value = [{
            "recordId": 1,
            "polymerProperty": {"polymerComponents": [{"polymerName": "PAN"}]}
        }]
        mock_request.return_value = mock_response

        df = self.client.download_latest(filters={"polymer": "PAN"})
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["polymer(s)"], "PAN")
        
        # Verify call parameters
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], "https://api.example.com/export")
        self.assertEqual(kwargs["params"]["format"], "json")
        self.assertEqual(json.loads(kwargs["params"]["filter"]), {"polymer": "PAN"})

    @patch('requests.Session.request')
    def test_api_error_handling(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid filter"}
        mock_request.return_value = mock_response

        with self.assertRaises(APIError) as cm:
            self.client.download_latest(filters={"invalid": "filter"})
        
        self.assertIn("Invalid filter", str(cm.exception))
        self.assertEqual(cm.exception.status_code, 400)

    @patch('requests.Session.request')
    def test_load_records_paginated(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": [], "total": 0}
        mock_request.return_value = mock_response

        result = self.client.load_records(skip=10, limit=20)
        
        self.assertEqual(result["total"], 0)
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["params"]["skip"], 10)
        self.assertEqual(kwargs["params"]["limit"], 20)

    def tearDown(self):
        self.client.close()

if __name__ == '__main__':
    unittest.main()
