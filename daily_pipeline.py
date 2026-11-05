import io
import logging
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
from google.cloud import bigquery, storage

# Google Cloud configuration
PROJECT_ID = "austin-311-data-pipeline"
BUCKET_NAME = "austin-311-data-pipeline-110426"
BIGQUERY_LOCATION = "us-central1"

RAW_TABLE = (
    "austin-311-data-pipeline.austin_311.service_requests_raw"
)

GCS_FOLDER = "raw/incremental"
SQL_FOLDER = "sql"
STATE_FILE = "state/last_successful_run.txt"

# Austin 311 API
API_URL = "https://data.austintexas.gov/resource/xwdj-i9he.json"

# Incremental ingestion settings
PAGE_SIZE = 1000
OVERLAP_HOURS = 48
INITIAL_LOOKBACK_DAYS = 30

# SQL files run in this order
SQL_FILES = [
    "refresh_clean.sql",
    "refresh_monthly.sql",
    "refresh_daily_october.sql",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


def get_start_time(bucket):
    """Read the previous successful run timestamp from GCS."""

    state_blob = bucket.blob(STATE_FILE)

    if state_blob.exists():
        previous_run = datetime.fromisoformat(
            state_blob.download_as_text().strip()
        )

        return previous_run - timedelta(hours=OVERLAP_HOURS)

    return datetime.now(timezone.utc) - timedelta(
        days=INITIAL_LOOKBACK_DAYS
    )


def fetch_records(start_time):
    """Retrieve records updated since the specified timestamp."""

    all_records = []
    offset = 0

    start_text = start_time.strftime("%Y-%m-%dT%H:%M:%S")

    while True:
        params = {
            "$where": f"sr_updated_date >= '{start_text}'",
            "$order": "sr_updated_date ASC",
            "$limit": PAGE_SIZE,
            "$offset": offset,
        }

        response = requests.get(
            API_URL,
            params=params,
            timeout=60
        )

        response.raise_for_status()

        records = response.json()

        if not isinstance(records, list):
            raise ValueError("Unexpected API response.")

        all_records.extend(records)

        logging.info(
            "Retrieved %s records at offset %s",
            len(records),
            offset
        )

        if len(records) < PAGE_SIZE:
            break

        offset += PAGE_SIZE

    return all_records


def prepare_dataframe(df, raw_table):
    """Align incoming CSV columns with the existing BigQuery schema."""

    schema_names = [field.name for field in raw_table.schema]

    if "sr_number" not in df.columns:
        raise ValueError("Missing sr_number column.")

    missing_required = [
        field.name
        for field in raw_table.schema
        if field.mode == "REQUIRED" and field.name not in df.columns
    ]

    if missing_required:
        raise ValueError(
            f"Missing required BigQuery columns: {missing_required}"
        )

    extra_columns = [
        column for column in df.columns
        if column not in schema_names
    ]

    missing_columns = [
        column for column in schema_names
        if column not in df.columns
    ]

    if extra_columns:
        logging.warning("Ignoring API columns not in BigQuery: %s", extra_columns)

    if missing_columns:
        logging.warning("BigQuery columns missing from API response: %s", missing_columns)

    # Match the exact column order of the existing BigQuery table.
    return df.reindex(columns=schema_names)


def upload_to_gcs(bucket, df, run_started):
    """Upload the CSV batch directly to GCS and return its URI."""

    timestamp = run_started.strftime("%Y%m%dT%H%M%SZ")

    filename = f"austin_311_{timestamp}.csv"

    blob_name = f"{GCS_FOLDER}/{filename}"

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    blob = bucket.blob(blob_name)

    blob.upload_from_string(
        csv_buffer.getvalue(),
        content_type="text/csv"
    )

    gcs_uri = f"gs://{BUCKET_NAME}/{blob_name}"

    logging.info("Uploaded successfully: %s", gcs_uri)

    return gcs_uri


def load_to_bigquery(bq_client, gcs_uri, raw_table):
    """Append the uploaded CSV batch to the BigQuery raw table."""

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        schema=raw_table.schema,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        allow_quoted_newlines=True,
    )

    load_job = bq_client.load_table_from_uri(
        gcs_uri,
        RAW_TABLE,
        job_config=job_config,
        location=BIGQUERY_LOCATION,
    )

    load_job.result()

    logging.info(
        "BigQuery load completed. Rows loaded: %s",
        load_job.output_rows
    )


def execute_sql_files(bucket, bq_client):
    """Download and execute SQL transformations stored in GCS."""

    for filename in SQL_FILES:
        blob_name = f"{SQL_FOLDER}/{filename}"

        sql_blob = bucket.blob(blob_name)

        sql = sql_blob.download_as_text()

        logging.info("Executing SQL file: %s", filename)

        query_job = bq_client.query(
            sql,
            location=BIGQUERY_LOCATION
        )

        query_job.result()

        logging.info(
            "SQL completed successfully: %s",
            filename
        )


def update_watermark(bucket, run_started):
    """Save the successful run timestamp in GCS."""

    state_blob = bucket.blob(STATE_FILE)

    state_blob.upload_from_string(
        run_started.isoformat(),
        content_type="text/plain"
    )

    logging.info("GCS watermark updated: %s", run_started.isoformat())


def main():

    run_started = datetime.now(timezone.utc)

    try:
        # Connect using Cloud Run's attached service account.
        storage_client = storage.Client(project=PROJECT_ID)

        bq_client = bigquery.Client(
            project=PROJECT_ID,
            location=BIGQUERY_LOCATION
        )

        bucket = storage_client.bucket(BUCKET_NAME)

        # Determine incremental extraction start time.
        start_time = get_start_time(bucket)

        logging.info(
            "Retrieving records updated since: %s",
            start_time
        )

        # Retrieve records from Austin 311 API.
        records = fetch_records(start_time)

        if not records:
            logging.info("No new or updated records found.")

            update_watermark(bucket, run_started)

            return

        df = pd.DataFrame(records)

        logging.info("Records retrieved: %s", len(df))

        logging.info(
            "Unique request IDs: %s",
            df["sr_number"].nunique()
        )

        # Retrieve the existing BigQuery schema.
        raw_table = bq_client.get_table(RAW_TABLE)

        # Align CSV columns and their order with BigQuery.
        df = prepare_dataframe(df, raw_table)

        # Upload CSV to GCS.
        gcs_uri = upload_to_gcs(
            bucket,
            df,
            run_started
        )

        # Append CSV batch to BigQuery raw table.
        load_to_bigquery(
            bq_client,
            gcs_uri,
            raw_table
        )

        # Refresh clean and summary tables.
        execute_sql_files(
            bucket,
            bq_client
        )

        # Advance watermark only after all steps succeed.
        update_watermark(bucket, run_started)

        logging.info("Daily pipeline completed successfully.")

    except Exception:
        logging.exception("Daily pipeline failed.")
        raise


if __name__ == "__main__":
    main()
