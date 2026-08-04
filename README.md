# Electrospinning Data Client

A Python library for programmatic access to the [Electrospinning Data Public API](https://electrospinning-data.org).

## Features

- **Easy Data Retrieval**: Download the latest dataset directly into a pandas DataFrame.
- **Versioning Support**: Access specific immutable version snapshots for reproducible research.
- **Advanced Filtering**: Apply complex filters (string matches, numeric ranges) directly in your queries.
- **Multiple Formats**: Export data to XLSX, JSON, or download image archives (ZIP).
- **Researcher Friendly**: Designed for ease of use in Jupyter Notebooks and data science workflows.

## Installation

Install using pip:

```bash
pip install electrospinning-data-client
```

## Quick Start

### Load the Latest Dataset

```python
import electrospinning_data_client as ed

# Download the latest dataset as a pandas DataFrame
df = ed.load_latest_dataset()

print(f"Retrieved {len(df)} records")
print(df.head())
```

### Apply Filters

Recover PAN produced with voltage between 20 and 30 kV:

```python
filters = {
    "polymer": "PAN",
    "voltageMin": 20,
    "voltageMax": 30
}

df = ed.load_latest_dataset(filters=filters)
```

### Access Specific Versions

```python
# List available versions
client = ed.ElectrospinningDataClient()
versions = client.get_versions()

# Download a specific version
df_v1 = ed.load_versioned_dataset("v1.0.0")
```

### Export to Excel or ZIP

```python
client = ed.ElectrospinningDataClient()

# Export to Excel
client.export_file("my_data.xlsx", export_format="xlsx", filters={"polymer": "PAN"})

# Download image archive
client.export_file("images.zip", export_format="zip")
```

### Submitting Data

Submitting or updating experiment records requires a personal access token, created from your profile settings on [electrospinning-data.org](https://electrospinning-data.org) (Profile Settings → API Tokens):

```python
client = ed.ElectrospinningDataClient(api_token="esd_pat_your_token_here")

result = client.submit_experiment({
    "userMetadata": {"name": "Jane Doe", "email": "jane@example.com", "consentTerms": True},
    "researchMetadata": {"publicationTitle": "My study"},
    "experimentData": [{"polymerProperty": {}, "processParameter": {}}],
})
print(result["records"][0]["status"])  # "PENDING", or "NEEDS_UPDATE" if a mandatory field was missing
```

Missing a mandatory field (e.g. polymer information) doesn't raise an error — the record is saved with status `"NEEDS_UPDATE"` and `result["records"][0]["missingFields"]` tells you what to fill in. Complete it later with `update_experiment`:

```python
client.update_experiment(result["records"][0]["recordId"], {
    "userMetadata": {"name": "Jane Doe", "email": "jane@example.com", "consentTerms": True},
    "experimentData": [{"polymerProperty": {"polymerComponents": [{"polymerName": "PVA"}]}}],
})
# -> status flips back to "PENDING"
```

Query your own records by status - separately or all together:

```python
needs_update_ids = client.list_my_record_ids(status="NEEDS_UPDATE")  # ids only, cheap
needs_update_records = client.list_my_records(status="NEEDS_UPDATE")  # full data
all_my_records = client.list_my_records()  # every status combined
```

Reading/downloading the dataset never requires a token. See the [Authentication guide](https://electrospinning-data.org/docs/api/authentication) for details, record statuses, token expiry/revocation, and error handling.

## API Reference

### `ElectrospinningDataClient`

Main class for API interaction.

- `get_versions()`: Returns a list of available dataset versions.
- `download_latest(filters=None)`: Returns a pandas DataFrame of the latest records.
- `download_version(version, filters=None)`: Returns a pandas DataFrame for a specific version.
- `export_file(output_path, export_format='xlsx', version='latest', filters=None)`: Saves data to a local file.
- `load_records(skip=0, limit=100, version='latest', filters=None)`: Returns a raw dictionary of paginated records.
- `submit_experiment(payload)`: Submits a new experiment record. Requires `api_token`. Returns a dict with per-record `status`/`missingFields`; missing mandatory fields are saved as `NEEDS_UPDATE` rather than raising.
- `update_experiment(experiment_id, payload)`: Updates an existing experiment record. Requires `api_token`.
- `get_submission_status(submission_id)`: Retrieves the current status of a submission you own. Requires `api_token`.
- `list_my_records(status=None)`: Lists your own submitted records, optionally filtered to one status (`PENDING`/`APPROVED`/`REJECTED`/`NEEDS_UPDATE`), or every status if omitted. Requires `api_token`.
- `list_my_record_ids(status=None)`: Same filtering as `list_my_records`, but returns only record ids. Requires `api_token`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
