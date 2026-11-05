
import pandas as pd
from pathlib import Path

files = sorted(
    Path("data/incremental").glob("austin_311_*.csv")
)

if not files:
    raise FileNotFoundError("No incremental batches found.")

all_batches = []

for file in files:
    df = pd.read_csv(file)

    print(f"\nFile: {file.name}")
    print(f"Rows: {len(df)}")
    print(f"Unique IDs: {df['sr_number'].nunique()}")

    df["source_file"] = file.name
    all_batches.append(df)

combined = pd.concat(all_batches, ignore_index=True)

print("\n--- CROSS-BATCH VALIDATION ---")
print("Total rows across batches:", len(combined))
print("Unique request IDs:", combined["sr_number"].nunique())

duplicate_count = combined["sr_number"].duplicated().sum()

print("Repeated IDs across batches:", duplicate_count)

if duplicate_count > 0:
    repeated = combined[
        combined["sr_number"].duplicated(keep=False)
    ]

    print("\nSample repeated request IDs:")
    print(
        repeated[["sr_number", "source_file"]]
        .sort_values("sr_number")
        .head(20)
        .to_string(index=False)
    )
else:
    print("No repeated request IDs found across batches.")

# --- DUPLICATE RECORD VALIDATION ---

if duplicate_count > 0:

    repeated = combined[
        combined["sr_number"].duplicated(keep=False)
    ]

    # Exclude source_file when comparing business data
    comparison_columns = [
        col for col in combined.columns
        if col != "source_file"
    ]

    # Count distinct versions of each request
    version_counts = (
        repeated.groupby("sr_number")[comparison_columns]
        .apply(lambda group: len(group.drop_duplicates()))
    )

    identical_count = (version_counts == 1).sum()
    changed_count = (version_counts > 1).sum()

    print("\n--- DUPLICATE VALIDATION RESULTS ---")
    print("Duplicated request IDs:", len(version_counts))
    print("Identical records:", identical_count)
    print("Records with differences:", changed_count)

    if changed_count > 0:
        print("\nSample request IDs with differences:")
        print(version_counts[version_counts > 1].head(10))

else:
    print("\nNo duplicate records to validate.")
