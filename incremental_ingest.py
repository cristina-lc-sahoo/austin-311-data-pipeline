
import requests
import pandas as pd

from pathlib import Path
from datetime import datetime, timedelta, timezone

API_URL = "https://data.austintexas.gov/resource/xwdj-i9he.json"

DATA_DIR = Path("data/incremental")
STATE_FILE = Path("data/last_successful_run.txt")

PAGE_SIZE = 1000
OVERLAP_HOURS = 48
INITIAL_LOOKBACK_DAYS = 30


def get_start_time():
    """Get the previous successful run time or initial lookback date."""

    if STATE_FILE.exists():
        previous_run = datetime.fromisoformat(
            STATE_FILE.read_text().strip()
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

        print(f"Retrieved {len(records)} records at offset {offset}")

        if len(records) < PAGE_SIZE:
            break

        offset += PAGE_SIZE

    return all_records


def main():
    run_started = datetime.now(timezone.utc)

    try:
        start_time = get_start_time()

        print(f"Retrieving records updated since: {start_time}")

        records = fetch_records(start_time)

        if not records:
            print("No new or updated records found.")
        else:
            df = pd.DataFrame(records)

            DATA_DIR.mkdir(parents=True, exist_ok=True)

            timestamp = run_started.strftime("%Y%m%dT%H%M%SZ")

            output_file = DATA_DIR / f"austin_311_{timestamp}.csv"

            df.to_csv(output_file, index=False)

            print(f"\nRecords retrieved: {len(df)}")
            print(f"Unique request IDs: {df['sr_number'].nunique()}")
            print(f"Saved batch: {output_file}")

        # Advance watermark only after successful retrieval and saving.
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(run_started.isoformat())

        print("\nIncremental ingestion completed successfully.")

    except Exception as error:
        print(f"\nIncremental ingestion failed: {error}")
        raise


if __name__ == "__main__":
    main()

