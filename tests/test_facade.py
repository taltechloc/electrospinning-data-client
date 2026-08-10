"""
Tests for the `Client` facade: the short, ergonomic API added on top of the
existing `ElectrospinningDataClient` methods.

These tests deliberately don't re-test business logic already covered by
test_client.py / test_submission.py / test_integration.py (URL construction,
error mapping, NEEDS_UPDATE server behavior, etc.) - they verify that the new
short methods are thin, correct wrappers around that existing, already-tested
behavior, and that nothing about the old API changed.
"""
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from electrospinning_data_client import Client, ElectrospinningDataClient, FilterBuilder


def _mock_ok(json_value=None, content=None):
    mock_response = MagicMock()
    mock_response.ok = True
    if content is not None:
        mock_response.content = content
    else:
        mock_response.json.return_value = json_value
    return mock_response


class TestBackwardCompatibility(unittest.TestCase):
    """`Client` is the new name; `ElectrospinningDataClient` must keep working exactly as before."""

    def test_electrospinning_data_client_is_the_same_class_as_client(self):
        # Not a subclass or a copy - the literal same class object, so
        # isinstance() checks against the old name keep working forever.
        self.assertIs(ElectrospinningDataClient, Client)

    def test_old_class_name_still_constructs_and_works(self):
        client = ElectrospinningDataClient(base_url="https://api.example.com")
        self.assertIsInstance(client, Client)
        client.close()

    def test_old_api_token_kwarg_still_authenticates_write_calls(self):
        client = Client(base_url="https://api.example.com", api_token="esd_pat_old_style")

        with patch('requests.Session.request') as mock_request:
            mock_request.return_value = _mock_ok({"submissionId": 1, "records": []})
            client.submit_experiment({"userMetadata": {"name": "A"}})

        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer esd_pat_old_style")

    def test_all_pre_existing_method_names_are_still_present(self):
        client = Client(base_url="https://api.example.com")
        for name in [
            "download_latest", "download_version", "get_versions", "export_file",
            "load_records", "submit_experiment", "update_experiment",
            "get_submission_status", "list_my_records", "list_my_record_ids", "close",
        ]:
            self.assertTrue(hasattr(client, name), f"missing pre-existing method: {name}")


class TestTokenParameter(unittest.TestCase):
    """`token=` is the new preferred kwarg; `api_token=` keeps working; `token` wins if both are given."""

    def test_token_kwarg_authenticates_write_calls(self):
        client = Client(base_url="https://api.example.com", token="esd_pat_new_style")

        with patch('requests.Session.request') as mock_request:
            mock_request.return_value = _mock_ok({"submissionId": 1, "records": []})
            client.submit({"userMetadata": {"name": "A"}})

        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer esd_pat_new_style")

    def test_token_takes_precedence_over_api_token_when_both_given(self):
        client = Client(base_url="https://api.example.com", token="new", api_token="old")

        with patch('requests.Session.request') as mock_request:
            mock_request.return_value = _mock_ok({"submissionId": 1, "records": []})
            client.submit({"userMetadata": {"name": "A"}})

        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer new")

    def test_no_token_raises_authentication_error_on_write(self):
        from electrospinning_data_client import AuthenticationError
        client = Client(base_url="https://api.example.com")
        with self.assertRaises(AuthenticationError):
            client.submit({"userMetadata": {"name": "A"}})


class TestShortMethods(unittest.TestCase):
    """submit/update/status/records/record_ids/versions must call exactly the same
    endpoints as their long-named counterparts."""

    def setUp(self):
        self.client = Client(base_url="https://api.example.com", token="esd_pat_test")

    def tearDown(self):
        self.client.close()

    @patch('requests.Session.request')
    def test_submit_delegates_to_submit_experiment(self, mock_request):
        mock_request.return_value = _mock_ok({
            "submissionId": 7,
            "records": [{"recordId": 100, "status": "PENDING", "missingFields": []}],
        })

        payload = {"userMetadata": {"name": "Jane"}}
        result = self.client.submit(payload)

        self.assertEqual(result["submissionId"], 7)
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "https://api.example.com/data/submit")
        self.assertEqual(kwargs["json"], payload)

    @patch('requests.Session.request')
    def test_update_delegates_to_update_experiment(self, mock_request):
        mock_request.return_value = _mock_ok(
            {"recordId": 42, "status": "PENDING", "missingFields": [], "message": "ok"}
        )

        result = self.client.update(42, {"userMetadata": {"name": "Jane"}})

        self.assertEqual(result["recordId"], 42)
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "PUT")
        self.assertEqual(args[1], "https://api.example.com/data/update/42")

    @patch('requests.Session.request')
    def test_status_delegates_to_get_submission_status(self, mock_request):
        mock_request.return_value = _mock_ok({"submissionId": 8, "status": "PENDING"})

        result = self.client.status(8)

        self.assertEqual(result["status"], "PENDING")
        args, _ = mock_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], "https://api.example.com/data/submission/8")

    @patch('requests.Session.request')
    def test_records_delegates_to_list_my_records(self, mock_request):
        mock_request.return_value = _mock_ok([{"recordId": 1, "status": "NEEDS_UPDATE"}])

        result = self.client.records(status="NEEDS_UPDATE")

        self.assertEqual(result, [{"recordId": 1, "status": "NEEDS_UPDATE"}])
        args, kwargs = mock_request.call_args
        self.assertEqual(args[1], "https://api.example.com/data/my-records")
        self.assertEqual(kwargs["params"], {"status": "NEEDS_UPDATE"})

    @patch('requests.Session.request')
    def test_records_without_status_returns_everything(self, mock_request):
        mock_request.return_value = _mock_ok([
            {"recordId": 1, "status": "PENDING"},
            {"recordId": 2, "status": "NEEDS_UPDATE"},
        ])

        result = self.client.records()

        self.assertEqual(len(result), 2)
        _, kwargs = mock_request.call_args
        self.assertIsNone(kwargs["params"])

    @patch('requests.Session.request')
    def test_record_ids_delegates_to_list_my_record_ids(self, mock_request):
        mock_request.return_value = _mock_ok([2, 5, 9])

        result = self.client.record_ids(status="NEEDS_UPDATE")

        self.assertEqual(result, [2, 5, 9])
        args, kwargs = mock_request.call_args
        self.assertEqual(args[1], "https://api.example.com/data/my-records/ids")
        self.assertEqual(kwargs["params"], {"status": "NEEDS_UPDATE"})

    @patch('requests.Session.request')
    def test_versions_delegates_to_get_versions(self, mock_request):
        mock_request.return_value = _mock_ok([
            {"versionIdentifier": "v1.0.0", "recordCount": 100, "createdAt": "2024-01-01"}
        ])

        result = self.client.versions()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].version_identifier, "v1.0.0")
        args, _ = mock_request.call_args
        self.assertEqual(args[1], "https://api.example.com/versions")


class TestDownload(unittest.TestCase):
    """`download()` must default to the latest snapshot and route to the
    versioned endpoint when a version is given - matching `download_latest`
    and `download_version` exactly."""

    def setUp(self):
        self.client = Client(base_url="https://api.example.com")

    def tearDown(self):
        self.client.close()

    @patch('requests.Session.request')
    def test_download_with_no_args_fetches_latest(self, mock_request):
        mock_request.return_value = _mock_ok([
            {"recordId": 1, "polymerProperty": {"polymerComponents": [{"polymerName": "PAN"}]}}
        ])

        df = self.client.download()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        args, kwargs = mock_request.call_args
        self.assertEqual(args[1], "https://api.example.com/export")
        self.assertEqual(kwargs["params"]["format"], "json")

    @patch('requests.Session.request')
    def test_download_with_version_hits_versioned_endpoint(self, mock_request):
        mock_request.return_value = _mock_ok([])

        self.client.download(version="v1.0.0")

        args, _ = mock_request.call_args
        self.assertEqual(args[1], "https://api.example.com/v1.0.0/export")

    @patch('requests.Session.request')
    def test_download_version_latest_is_equivalent_to_no_version(self, mock_request):
        mock_request.return_value = _mock_ok([])

        self.client.download(version="latest")

        args, _ = mock_request.call_args
        self.assertEqual(args[1], "https://api.example.com/export")

    @patch('requests.Session.request')
    def test_download_with_doi_version_uses_query_param_not_path(self, mock_request):
        """DOIs contain '/', which the /{version}/export path can't carry -
        must be routed through /export?version=<doi> instead."""
        mock_request.return_value = _mock_ok([])

        self.client.download(version="10.5281/zenodo.1234567")

        args, kwargs = mock_request.call_args
        self.assertEqual(args[1], "https://api.example.com/export")
        self.assertEqual(kwargs["params"]["version"], "10.5281/zenodo.1234567")

    @patch('requests.Session.request')
    def test_download_applies_filters(self, mock_request):
        mock_request.return_value = _mock_ok([])

        self.client.download(filters={"polymer": "PAN"})

        _, kwargs = mock_request.call_args
        self.assertIn("filter", kwargs["params"])


class TestSearch(unittest.TestCase):
    """`search()` is filter-first sugar over the same dataset export endpoint as `download()`."""

    def setUp(self):
        self.client = Client(base_url="https://api.example.com")

    def tearDown(self):
        self.client.close()

    @patch('requests.Session.request')
    def test_search_applies_dict_filters(self, mock_request):
        mock_request.return_value = _mock_ok([
            {"recordId": 1, "polymerProperty": {"polymerComponents": [{"polymerName": "PAN"}]}}
        ])

        df = self.client.search(filters={"polymer": "PAN"})

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        args, kwargs = mock_request.call_args
        self.assertEqual(args[1], "https://api.example.com/export")
        self.assertEqual(kwargs["params"]["filter"], '{"polymer": "PAN"}')

    @patch('requests.Session.request')
    def test_search_accepts_filter_builder(self, mock_request):
        mock_request.return_value = _mock_ok([])

        self.client.search(filters=FilterBuilder().polymer("PAN").voltage(min_val=20).build())

        _, kwargs = mock_request.call_args
        self.assertIn("PAN", kwargs["params"]["filter"])

    @patch('requests.Session.request')
    def test_search_against_specific_version(self, mock_request):
        mock_request.return_value = _mock_ok([])

        self.client.search(filters={"polymer": "PAN"}, version="v2.0.0")

        args, _ = mock_request.call_args
        self.assertEqual(args[1], "https://api.example.com/v2.0.0/export")

    @patch('requests.Session.request')
    def test_search_with_no_filters_returns_full_dataset(self, mock_request):
        mock_request.return_value = _mock_ok([{"recordId": 1}, {"recordId": 2}])

        df = self.client.search()

        self.assertEqual(len(df), 2)


class TestNeedsUpdateStillHandledTheSameWay(unittest.TestCase):
    """The facade must not change NEEDS_UPDATE semantics: it's a normal, successful
    result (no exception), and update() flips it back to PENDING - exactly like
    submit_experiment/update_experiment already do."""

    def setUp(self):
        self.client = Client(base_url="https://api.example.com", token="esd_pat_test")

    def tearDown(self):
        self.client.close()

    @patch('requests.Session.request')
    def test_submit_with_missing_mandatory_field_returns_needs_update_not_an_exception(self, mock_request):
        mock_request.return_value = _mock_ok({
            "message": "Data submitted successfully",
            "submissionId": 8,
            "records": [{
                "recordId": 101,
                "status": "NEEDS_UPDATE",
                "missingFields": ["polymerProperty"],
            }],
        })

        result = self.client.submit({
            "userMetadata": {"name": "A", "email": "a@example.com", "consentTerms": True},
            "experimentData": [{"processParameter": {"voltage": 20}}],
        })

        self.assertEqual(result["records"][0]["status"], "NEEDS_UPDATE")
        self.assertIn("polymerProperty", result["records"][0]["missingFields"])

    @patch('requests.Session.request')
    def test_update_completing_needs_update_record_flips_to_pending(self, mock_request):
        mock_request.return_value = _mock_ok({
            "recordId": 101, "status": "PENDING", "missingFields": [], "message": "updated",
        })

        result = self.client.update(101, {
            "experimentData": [{"polymerProperty": {"polymerComponents": [{"polymerName": "PVA"}]}}],
        })

        self.assertEqual(result["status"], "PENDING")
        self.assertEqual(result["missingFields"], [])

    @patch('requests.Session.request')
    def test_status_reports_needs_update_for_incomplete_submission(self, mock_request):
        mock_request.return_value = _mock_ok({
            "submissionId": 8,
            "status": "NEEDS_UPDATE",
            "experimentData": [{"recordId": 101, "status": "NEEDS_UPDATE"}],
        })

        result = self.client.status(8)

        self.assertEqual(result["status"], "NEEDS_UPDATE")

    @patch('requests.Session.request')
    def test_record_ids_can_be_used_to_find_incomplete_records(self, mock_request):
        mock_request.return_value = _mock_ok([101, 102])

        ids = self.client.record_ids(status="NEEDS_UPDATE")

        self.assertEqual(ids, [101, 102])
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["params"], {"status": "NEEDS_UPDATE"})


if __name__ == "__main__":
    unittest.main()
