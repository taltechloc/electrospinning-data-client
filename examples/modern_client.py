"""
Example showing the modern, short-method `Client` API end-to-end: downloading,
searching, and (if a token is configured) submitting/updating/checking on data.

This is equivalent to the older, more verbose style shown in the other
examples in this directory (`ed.load_latest_dataset()`,
`client.submit_experiment(...)`, etc.) - both keep working, this is just the
shorter spelling.

Write operations (submit/update/status) default to the SANDBOX environment
here on purpose: it's isolated from production, safe to write disposable test
data to, and exactly what you want while developing an integration. Create a
sandbox token from Profile Settings on the website (its prefix is
`esd_sandbox_...`) and set ESD_SANDBOX_TOKEN before running this.

Once your integration is verified against sandbox, promote it to production
by creating a production token (`esd_pat_...`) and changing
`environment="sandbox"` to `environment="production"` below - nothing else
about this example needs to change.
"""
import os

from electrospinning_data_client import AuthenticationError, Client


def main():
    # Reading/downloading never requires a token. Pass one (e.g. via an env
    # var) to also use submit()/update()/status()/records()/record_ids().
    # `environment="sandbox"` here is what routes those write calls to
    # sandbox-api.electrospinning-data.org instead of production.
    client = Client(token=os.environ.get("ESD_SANDBOX_TOKEN"), environment="sandbox")

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
        print("No ESD_SANDBOX_TOKEN set - skipping submit/update/status/records examples.")
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
