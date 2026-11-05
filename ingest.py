
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

API_URL = "https://data.austintexas.gov/resource/xwdj-i9he.json"


def fetch_service_requests(limit=100):
    params = {
        "$limit": limit,
        "$order": "sr_created_date DESC",
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    records = response.json()

    if not isinstance(records, list):
        raise ValueError("Expected a list of records from the API.")

    return records


def main():
    try:
        records = fetch_service_requests(limit=100)

        if not records:
            print("No records returned.")
            return

        df = pd.DataFrame(records)

        output_dir = Path("data")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_file = output_dir / f"austin_311_{timestamp}.csv"

        df.to_csv(output_file, index=False)

        print(f"Records retrieved: {len(df)}")
        print(f"Columns retrieved: {len(df.columns)}")
        print(f"CSV saved to: {output_file}")
        print("\nFirst five records:")
        print(df.head().to_string(index=False))

    except (requests.RequestException, ValueError) as error:
        print(f"Ingestion failed: {error}")


if __name__ == "__main__":
    main()

