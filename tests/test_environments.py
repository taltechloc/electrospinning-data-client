import unittest
from unittest.mock import MagicMock, patch

from electrospinning_data_client import (
    Client,
    EnvironmentMismatchError,
    PRODUCTION,
    SANDBOX,
)


class TestClientEnvironmentResolution(unittest.TestCase):

    def test_no_args_keeps_historical_default(self):
        client = Client()
        self.assertEqual(client.base_url, "https://api.electrospinning-data.org/public/dataset")
        self.assertEqual(client.api_base_url, "https://api.electrospinning-data.org")
        self.assertIsNone(client.environment)

    def test_environment_sandbox_resolves_sandbox_urls(self):
        client = Client(environment="sandbox")
        self.assertEqual(client.base_url, "https://sandbox-api.electrospinning-data.org/public/dataset")
        self.assertEqual(client.api_base_url, "https://sandbox-api.electrospinning-data.org")
        self.assertEqual(client.environment, SANDBOX)

    def test_environment_production_resolves_production_urls(self):
        client = Client(environment="production")
        self.assertEqual(client.base_url, "https://api.electrospinning-data.org/public/dataset")
        self.assertEqual(client.api_base_url, "https://api.electrospinning-data.org")
        self.assertEqual(client.environment, PRODUCTION)

    def test_environment_is_case_insensitive(self):
        client = Client(environment="SANDBOX")
        self.assertEqual(client.environment, SANDBOX)

    def test_unknown_environment_raises_value_error(self):
        with self.assertRaises(ValueError):
            Client(environment="staging")

    def test_explicit_base_url_overrides_environment(self):
        client = Client(base_url="https://custom.example.com/public/dataset", environment="sandbox")
        self.assertEqual(client.base_url, "https://custom.example.com/public/dataset")
        # api_base_url still derives from environment since it wasn't explicitly given
        self.assertEqual(client.api_base_url, "https://sandbox-api.electrospinning-data.org")

    def test_explicit_api_base_url_overrides_environment(self):
        client = Client(environment="sandbox", api_base_url="https://custom-root.example.com")
        self.assertEqual(client.api_base_url, "https://custom-root.example.com")
        # base_url still derives from environment since it wasn't explicitly given
        self.assertEqual(client.base_url, "https://sandbox-api.electrospinning-data.org/public/dataset")

    def test_explicit_base_url_alone_does_not_set_environment_label(self):
        client = Client(base_url="https://custom.example.com/public/dataset")
        self.assertIsNone(client.environment)


class TestEnvironmentMismatchGuard(unittest.TestCase):

    def test_sandbox_token_against_production_environment_raises_before_request(self):
        client = Client(token="esd_sandbox_abc123", environment="production")
        with patch('requests.Session.request') as mock_request:
            with self.assertRaises(EnvironmentMismatchError):
                client.submit({"userMetadata": {"name": "A"}})
            mock_request.assert_not_called()

    def test_production_token_against_sandbox_environment_raises_before_request(self):
        client = Client(token="esd_pat_abc123", environment="sandbox")
        with patch('requests.Session.request') as mock_request:
            with self.assertRaises(EnvironmentMismatchError):
                client.submit({"userMetadata": {"name": "A"}})
            mock_request.assert_not_called()

    @patch('requests.Session.request')
    def test_matching_sandbox_token_and_environment_does_not_raise(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"message": "ok", "submissionId": 1, "records": []}
        mock_request.return_value = mock_response

        client = Client(token="esd_sandbox_abc123", environment="sandbox")
        client.submit({"userMetadata": {"name": "A"}})

        args, kwargs = mock_request.call_args
        self.assertEqual(args[1], "https://sandbox-api.electrospinning-data.org/data/submit")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer esd_sandbox_abc123")

    @patch('requests.Session.request')
    def test_matching_production_token_and_environment_does_not_raise(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"message": "ok", "submissionId": 1, "records": []}
        mock_request.return_value = mock_response

        client = Client(token="esd_pat_abc123", environment="production")
        client.submit({"userMetadata": {"name": "A"}})

        args, kwargs = mock_request.call_args
        self.assertEqual(args[1], "https://api.electrospinning-data.org/data/submit")

    @patch('requests.Session.request')
    def test_custom_base_url_skips_mismatch_check(self, mock_request):
        # A sandbox-prefixed token against an unrecognized custom host: the
        # check can't determine the URL's environment, so it stays silent --
        # the server remains the authoritative check.
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"message": "ok", "submissionId": 1, "records": []}
        mock_request.return_value = mock_response

        client = Client(token="esd_sandbox_abc123", base_url="https://localhost:8080/public/dataset")
        client.submit({"userMetadata": {"name": "A"}})  # must not raise

        mock_request.assert_called_once()

    def test_unrecognized_token_prefix_skips_mismatch_check(self):
        # A token that doesn't match either known prefix (e.g. a very old
        # token format) can't be classified, so the check stays silent.
        with patch('requests.Session.request') as mock_request:
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.json.return_value = {"message": "ok", "submissionId": 1, "records": []}
            mock_request.return_value = mock_response

            client = Client(token="some-legacy-token", environment="production")
            client.submit({"userMetadata": {"name": "A"}})  # must not raise
            mock_request.assert_called_once()


if __name__ == "__main__":
    unittest.main()
