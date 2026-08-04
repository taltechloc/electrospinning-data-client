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

    @patch('requests.Session.request')
    def test_submit_sends_bearer_token_to_derived_api_root(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = "Data submitted successfully"
        mock_request.return_value = mock_response

        client = ElectrospinningDataClient(
            base_url="https://api.example.com/public/dataset",
            api_token="esd_pat_testtoken123"
        )

        result = client.submit_experiment({"userMetadata": {"name": "A"}})

        self.assertEqual(result, "Data submitted successfully")
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "https://api.example.com/data/submit")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer esd_pat_testtoken123")
        self.assertEqual(kwargs["json"], {"userMetadata": {"name": "A"}})

    @patch('requests.Session.request')
    def test_update_sends_bearer_token_to_correct_url(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = "Updated"
        mock_request.return_value = mock_response

        client = ElectrospinningDataClient(
            base_url="https://api.example.com/public/dataset",
            api_token="esd_pat_testtoken123"
        )

        client.update_experiment(42, {"userMetadata": {"name": "A"}})

        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "PUT")
        self.assertEqual(args[1], "https://api.example.com/data/update/42")
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

    def test_explicit_api_base_url_overrides_derived_root(self):
        client = ElectrospinningDataClient(
            base_url="https://api.example.com/public/dataset",
            api_base_url="https://custom-root.example.com",
            api_token="esd_pat_x"
        )
        self.assertEqual(client.api_base_url, "https://custom-root.example.com")


if __name__ == "__main__":
    unittest.main()
