import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import json
import os
from electrospinning_data_client import (
    ElectrospinningDataClient, 
    APIError, 
    ValidationError,
    load_latest_dataset,
    load_versioned_dataset
)

class TestIntegrationStyle(unittest.TestCase):
    """
    Integration-style tests (mocking network but testing top-level functions).
    """

    @patch('requests.Session.request')
    def test_load_latest_dataset_convenience(self, mock_request):
        # Mocking a successful response for the export endpoint
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = [
            {"recordId": 1, "polymerProperty": {"polymerComponents": [{"polymerName": "PAN"}]}},
            {"recordId": 2, "polymerProperty": {"polymerComponents": [{"polymerName": "PAN"}]}}
        ]
        mock_request.return_value = mock_response

        # Call top-level convenience function
        df = load_latest_dataset(filters={"polymer": "PAN"})

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        
        # Verify that it correctly requested the export with format=json
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["params"]["format"], "json")
        self.assertEqual(json.loads(kwargs["params"]["filter"]), {"polymer": "PAN"})

    @patch('requests.Session.request')
    def test_export_file_functionality(self, mock_request):
        # Mocking binary file response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = b"fake-excel-content"
        mock_request.return_value = mock_response

        client = ElectrospinningDataClient()
        test_filename = "test_export.xlsx"
        
        try:
            client.export_file(test_filename, export_format="xlsx")
            
            # Verify file exists and has content
            self.assertTrue(os.path.exists(test_filename))
            with open(test_filename, "rb") as f:
                self.assertEqual(f.read(), b"fake-excel-content")
                
            # Verify request
            _, kwargs = mock_request.call_args
            self.assertEqual(kwargs["params"]["format"], "xlsx")
            
        finally:
            client.close()
            if os.path.exists(test_filename):
                os.remove(test_filename)

    @patch('requests.Session.request')
    def test_version_not_found(self, mock_request):
        # Mocking 404 for a missing version
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Version not found"
        # Mock json() to fail so it uses text
        mock_response.json.side_effect = ValueError("No JSON")
        mock_request.return_value = mock_response

        with self.assertRaises(APIError) as cm:
            load_versioned_dataset("invalid-v")
        
        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Version not found", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
