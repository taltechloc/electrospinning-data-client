"""
Example showing the modern, short-method `Client` API end-to-end: downloading,
searching, and (if a token is configured) submitting/updating/checking on data.

This is equivalent to the older, more verbose style shown in the other
examples in this directory (`ed.load_latest_dataset()`,
`client.submit_experiment(...)`, etc.) - both keep working, this is just the
shorter spelling.
"""
import os

from electrospinning_data_client import AuthenticationError, Client


def main():
    # Reading/downloading never requires a token. Pass one (e.g. via an env
    # var) to also use submit()/update()/status()/records()/record_ids().
    client = Client(token=os.environ.get("ESD_API_TOKEN"))

    print("Downloading the latest dataset...")
    df = client.download()
    print(f"Retrieved {len(df)} records.\n")

    print("Searching for PAN records...")
    pan_df = client.search(filters={"polymer": "PAN"})
    print(f"Found {len(pan_df)} PAN records.\n")

    print("Available dataset versions:")
    for v in client.versions():
        print(f"- {v.version_identifier} ({v.record_count} records)")

    try:
        print("\nSubmitting a new experiment record...")
        result = client.submit({
            "userMetadata": {"name": "Jane Doe", "email": "jane@example.com", "consentTerms": True},
            "researchMetadata": {"publicationTitle": "Example submission via the Python client"},
            "experimentData": [{"processParameter": {"voltage": 20}}],  # missing polymerProperty on purpose
        })
    except AuthenticationError:
        print("No ESD_API_TOKEN set - skipping submit/update/status/records examples.")
        return

    record = result["records"][0]
    print(f"Record {record['recordId']} saved with status {record['status']}.")

    if record["status"] == "NEEDS_UPDATE":
        print(f"Missing fields: {record['missingFields']} - completing it now...")
        client.update(record["recordId"], {
            "userMetadata": {"name": "Jane Doe", "email": "jane@example.com", "consentTerms": True},
            "experimentData": [{"polymerProperty": {"polymerComponents": [{"polymerName": "PVA"}]}}],
        })

    print("Submission status:", client.status(result["submissionId"])["status"])
    print("My NEEDS_UPDATE records:", client.record_ids(status="NEEDS_UPDATE"))


if __name__ == "__main__":
    main()
