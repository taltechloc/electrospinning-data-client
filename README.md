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

```python
from electrospinning_data_client import Client

client = Client(token="esd_pat_your_token_here")  # omit token for read-only use

df = client.download()                          # latest dataset as a pandas DataFrame
df = client.search(filters={"polymer": "PAN"})   # filtered query

result = client.submit(record)                   # submit a new experiment record
client.update(result["records"][0]["recordId"], record)  # fix up a NEEDS_UPDATE record
client.status(result["submissionId"])             # check on a submission
```

`Client` is the main entry point. Every method has a short, everyday name (`submit`, `update`,
`status`, `download`, `search`, `records`, `record_ids`, `versions`) that's a thin wrapper
around a longer, more descriptive one (`submit_experiment`, `update_experiment`,
`get_submission_status`, `download_latest`/`download_version`, `list_my_records`,
`list_my_record_ids`, `get_versions`) — both spellings call exactly the same code, so use
whichever reads best. See [Migrating from the old names](#migrating-from-the-old-names) below;
**nothing old is removed or deprecated** — existing code keeps working with no changes.

### Download the Latest Dataset

```python
from electrospinning_data_client import Client

client = Client()
df = client.download()

print(f"Retrieved {len(df)} records")
print(df.head())
```

### Filter / Search

Find PAN produced with voltage between 20 and 30 kV:

```python
df = client.search(filters={"polymer": "PAN", "voltageMin": 20, "voltageMax": 30})
```

`search()` and `download(filters=...)` do the same thing — `search` just reads better when
filtering is the point of the call:

```python
df = client.download(filters={"polymer": "PAN"})
```

### Access Specific Versions

```python
# List available versions
for v in client.versions():
    print(v.version_identifier, v.record_count)

# Download (or search) a specific, reproducible snapshot
df_v1 = client.download(version="v1.0.0")
df_v1_pan = client.search(filters={"polymer": "PAN"}, version="v1.0.0")
```

### Export to Excel or ZIP

```python
client.export_file("my_data.xlsx", export_format="xlsx", filters={"polymer": "PAN"})
client.export_file("images.zip", export_format="zip")  # image archive
```

### Submitting Data

Submitting or updating experiment records requires a personal access token, created from your profile settings on [electrospinning-data.org](https://electrospinning-data.org) (Profile Settings → API Tokens):

```python
client = Client(token="esd_pat_your_token_here")

result = client.submit({
    "userMetadata": {"name": "Jane Doe", "email": "jane@example.com", "consentTerms": True},
    "researchMetadata": {"publicationTitle": "My study"},
    "experimentData": [{"polymerProperty": {}, "processParameter": {}}],
})
print(result["records"][0]["status"])  # "PENDING", or "NEEDS_UPDATE" if a mandatory field was missing
```

Missing a mandatory field (e.g. polymer information) doesn't raise an error — the record is saved with status `"NEEDS_UPDATE"` and `result["records"][0]["missingFields"]` tells you what to fill in. Complete it later with `update`:

```python
client.update(result["records"][0]["recordId"], {
    "userMetadata": {"name": "Jane Doe", "email": "jane@example.com", "consentTerms": True},
    "experimentData": [{"polymerProperty": {"polymerComponents": [{"polymerName": "PVA"}]}}],
})
# -> status flips back to "PENDING"
```

Query your own records by status - separately or all together:

```python
needs_update_ids = client.record_ids(status="NEEDS_UPDATE")  # ids only, cheap
needs_update_records = client.records(status="NEEDS_UPDATE")  # full data
all_my_records = client.records()  # every status combined
```

Reading/downloading the dataset never requires a token. See the [Authentication guide](https://electrospinning-data.org/docs/api/authentication) for details, record statuses, token expiry/revocation, and error handling.

## Migrating from the old names

There's no rush and no deadline — old names are not deprecated and will keep working. This is
just a lookup table if you'd like to adopt the shorter style:

| Old (still works) | New | Notes |
| :--- | :--- | :--- |
| `ElectrospinningDataClient(api_token=...)` | `Client(token=...)` | `ElectrospinningDataClient` is an alias for `Client`; `api_token` still works too. |
| `client.submit_experiment(payload)` | `client.submit(payload)` | Same behavior, including `NEEDS_UPDATE`. |
| `client.update_experiment(id, payload)` | `client.update(id, payload)` | |
| `client.get_submission_status(id)` | `client.status(id)` | |
| `client.download_latest(filters=None)` | `client.download()` | |
| `client.download_version(version, filters=None)` | `client.download(version=version)` | |
| `client.download_latest(filters={...})` | `client.search(filters={...})` | `search` is filter-first sugar over the same call. |
| `client.list_my_records(status=None)` | `client.records(status=None)` | |
| `client.list_my_record_ids(status=None)` | `client.record_ids(status=None)` | |
| `client.get_versions()` | `client.versions()` | |
| `load_latest_dataset()` / `load_versioned_dataset(v)` | *(unchanged)* | Still available as module-level one-shot functions. |

## API Reference

### `Client` (alias: `ElectrospinningDataClient`)

Main class for API interaction. `token` (preferred) / `api_token` (legacy) is only required for
the write/query-your-own-data methods; every read/download method works without it.

Short methods:

- `download(version=None, filters=None)`: Latest dataset (or a specific version) as a pandas DataFrame.
- `search(filters=None, version="latest")`: Filtered dataset query as a pandas DataFrame.
- `submit(record)`: Submit a new experiment record. Returns per-record `status`/`missingFields`; missing mandatory fields are saved as `NEEDS_UPDATE` rather than raising.
- `update(id, record)`: Update an existing experiment record.
- `status(submission_id)`: Current state of a submission you own.
- `records(status=None)`: Your own submitted records, optionally filtered to one status.
- `record_ids(status=None)`: Same as `records`, ids only.
- `versions()`: All available dataset version snapshots.

Full names (equivalent, unchanged):

- `get_versions()`: Returns a list of available dataset versions.
- `download_latest(filters=None)`: Returns a pandas DataFrame of the latest records.
- `download_version(version, filters=None)`: Returns a pandas DataFrame for a specific version.
- `export_file(output_path, export_format='xlsx', version='latest', filters=None)`: Saves data to a local file.
- `load_records(skip=0, limit=100, version='latest', filters=None)`: Returns a raw dictionary of paginated records.
- `submit_experiment(payload)`: Submits a new experiment record. Requires a token.
- `update_experiment(experiment_id, payload)`: Updates an existing experiment record. Requires a token.
- `get_submission_status(submission_id)`: Retrieves the current status of a submission you own. Requires a token.
- `list_my_records(status=None)`: Lists your own submitted records, optionally filtered to one status (`PENDING`/`APPROVED`/`REJECTED`/`NEEDS_UPDATE`), or every status if omitted. Requires a token.
- `list_my_record_ids(status=None)`: Same filtering as `list_my_records`, but returns only record ids. Requires a token.
- `close()`: Closes the underlying HTTP session.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
