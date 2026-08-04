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
```

Reading/downloading the dataset never requires a token. See the [Authentication guide](https://electrospinning-data.org/docs/api/authentication) for details, token expiry/revocation, and error handling.

## API Reference

### `ElectrospinningDataClient`

Main class for API interaction.

- `get_versions()`: Returns a list of available dataset versions.
- `download_latest(filters=None)`: Returns a pandas DataFrame of the latest records.
- `download_version(version, filters=None)`: Returns a pandas DataFrame for a specific version.
- `export_file(output_path, export_format='xlsx', version='latest', filters=None)`: Saves data to a local file.
- `load_records(skip=0, limit=100, version='latest', filters=None)`: Returns a raw dictionary of paginated records.
- `submit_experiment(payload)`: Submits a new experiment record. Requires `api_token`.
- `update_experiment(experiment_id, payload)`: Updates an existing experiment record. Requires `api_token`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
