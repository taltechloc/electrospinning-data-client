import unittest
from unittest.mock import MagicMock, patch

from electrospinning_data_client import ElectrospinningDataClient, APIError, AuthenticationError


class TestSubmissionService(unittest.TestCase):

    def test_submit_without_token_raises_authentication_error_before_any_request(self):
        client = ElectrospinningDataClient(base_url="https://api.example.com/public/dataset")

        with patch('requests.Session.request') as mock_request:
            with self.assertRaises(AuthenticationError):
                client.submit_experiment({"userMetadata": {"name": "A"}})
            mock_request.assert_not_called()

    def test_update_without_token_raises_authentication_error(self):
        client = ElectrospinningDataClient(base_url="https://api.example.com/public/dataset")

        with self.assertRaises(AuthenticationError):
            client.update_experiment(1, {"userMetadata": {"name": "A"}})

    def test_get_submission_status_without_token_raises_authentication_error(self):
        client = ElectrospinningDataClient(base_url="https://api.example.com/public/dataset")

        with self.assertRaises(AuthenticationError):
            client.get_submission_status(123)

    @patch('requests.Session.request')
    def test_submit_sends_bearer_token_to_derived_api_root(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "message": "Data submitted successfully",
            "submissionId": 7,
            "records": [{"recordId": 100, "status": "PENDING", "missingFields": []}],
        }
        mock_request.return_value = mock_response

        client = ElectrospinningDataClient(
            base_url="https://api.example.com/public/dataset",
            api_token="esd_pat_testtoken123"
        )

        result = client.submit_experiment({"userMetadata": {"name": "A"}})

        self.assertEqual(result["submissionId"], 7)
        self.assertEqual(result["records"][0]["status"], "PENDING")
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "https://api.example.com/data/submit")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer esd_pat_testtoken123")
        self.assertEqual(kwargs["json"], {"userMetadata": {"name": "A"}})

    @patch('requests.Session.request')
    def test_incomplete_submission_returns_needs_update_without_raising(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "message": "Data submitted successfully",
            "submissionId": 8,
            "records": [{
                "recordId": 101,
                "status": "NEEDS_UPDATE",
                "missingFields": ["polymerProperty"],
            }],
        }
        mock_request.return_value = mock_response

        client = ElectrospinningDataClient(
            base_url="https://api.example.com/public/dataset",
            api_token="esd_pat_testtoken123"
        )

        # A partial payload missing polymerProperty - must NOT raise.
        result = client.submit_experiment({
            "userMetadata": {"name": "A", "email": "a@example.com", "consentTerms": True},
            "researchMetadata": {},
            "experimentData": [{}],
        })

        self.assertEqual(result["records"][0]["status"], "NEEDS_UPDATE")
        self.assertIn("polymerProperty", result["records"][0]["missingFields"])

    @patch('requests.Session.request')
    def test_update_sends_bearer_token_to_correct_url(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "recordId": 42,
            "status": "PENDING",
            "missingFields": [],
            "message": "Experiment updated successfully",
        }
        mock_request.return_value = mock_response

        client = ElectrospinningDataClient(
            base_url="https://api.example.com/public/dataset",
            api_token="esd_pat_testtoken123"
        )

        result = client.update_experiment(42, {"userMetadata": {"name": "A"}})

        self.assertEqual(result["status"], "PENDING")
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "PUT")
        self.assertEqual(args[1], "https://api.example.com/data/update/42")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer esd_pat_testtoken123")

    @patch('requests.Session.request')
    def test_update_completing_needs_update_record_flips_to_pending(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "recordId": 101,
            "status": "PENDING",
            "missingFields": [],
            "message": "Experiment updated successfully",
        }
        mock_request.return_value = mock_response

        client = ElectrospinningDataClient(
            base_url="https://api.example.com/public/dataset",
            api_token="esd_pat_testtoken123"
        )

        result = client.update_experiment(101, {
            "userMetadata": {"name": "A", "email": "a@example.com", "consentTerms": True},
            "experimentData": [{"polymerProperty": {"polymerComponents": [{"polymerName": "PVA"}]}}],
        })

        self.assertEqual(result["status"], "PENDING")
        self.assertEqual(result["missingFields"], [])

    @patch('requests.Session.request')
    def test_get_submission_status_returns_parsed_json(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "submissionId": 8,
            "status": "NEEDS_UPDATE",
            "experimentData": [{"recordId": 101, "status": "NEEDS_UPDATE"}],
        }
        mock_request.return_value = mock_response

        client = ElectrospinningDataClient(
            base_url="https://api.example.com/public/dataset",
            api_token="esd_pat_testtoken123"
        )

        result = client.get_submission_status(8)

        self.assertEqual(result["status"], "NEEDS_UPDATE")
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], "https://api.example.com/data/submission/8")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer esd_pat_testtoken123")

    @patch('requests.Session.request')
    def test_revoked_token_surfaces_as_api_error_with_server_message(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "success": False,
            "message": "This API token has been revoked.",
            "code": "TOKEN_REVOKED"
        }
        mock_response.text = '{"success": false, "message": "This API token has been revoked.", "code": "TOKEN_REVOKED"}'
        mock_request.return_value = mock_response

        client = ElectrospinningDataClient(
            base_url="https://api.example.com/public/dataset",
            api_token="esd_pat_revoked"
        )

        with self.assertRaises(APIError) as ctx:
            client.submit_experiment({"userMetadata": {"name": "A"}})

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertIn("revoked", str(ctx.exception))

    @patch('requests.Session.request')
    def test_invalid_polymer_reference_surfaces_as_api_error(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Polymer not found: Unobtainium"}
        mock_response.text = '{"message": "Polymer not found: Unobtainium"}'
        mock_request.return_value = mock_response

        client = ElectrospinningDataClient(
            base_url="https://api.example.com/public/dataset",
            api_token="esd_pat_testtoken123"
        )

        with self.assertRaises(APIError) as ctx:
            client.submit_experiment({
                "experimentData": [{"polymerProperty": {"polymerComponents": [{"polymerName": "Unobtainium"}]}}],
            })

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Polymer not found", str(ctx.exception))

    def test_explicit_api_base_url_overrides_derived_root(self):
        client = ElectrospinningDataClient(
            base_url="https://api.example.com/public/dataset",
            api_base_url="https://custom-root.example.com",
            api_token="esd_pat_x"
        )
        self.assertEqual(client.api_base_url, "https://custom-root.example.com")


if __name__ == "__main__":
    unittest.main()
