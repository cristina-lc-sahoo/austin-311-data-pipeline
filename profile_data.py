
import pandas as pd
from pathlib import Path

# Find the latest ingested CSV
files = sorted(Path("data").glob("austin_311_*.csv"))

if not files:
    raise FileNotFoundError("No Austin 311 CSV files found.")

df = pd.read_csv(files[-1])

print("\n--- DATASET OVERVIEW ---")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- DATA TYPES ---")
print(df.dtypes)

print("\n--- MISSING VALUES ---")
print(df.isnull().sum().sort_values(ascending=False))

print("\n--- DUPLICATE RECORDS ---")
if "sr_number" in df.columns:
    print(f"Duplicate service request numbers: {df['sr_number'].duplicated().sum()}")


print("\n--- REQUEST STATUS SUMMARY ---")
print(df["sr_status_desc"].value_counts(dropna=False))

print("\n--- DEPARTMENT SUMMARY ---")
print(df["sr_department_desc"].value_counts().head(10))

print("\n--- REQUEST DATE RANGE ---")
df["sr_created_date"] = pd.to_datetime(
    df["sr_created_date"], errors="coerce"
)

print("Earliest request:", df["sr_created_date"].min())
print("Latest request:", df["sr_created_date"].max())

print("\n--- COORDINATE VALIDATION ---")
valid_coordinates = (
    df["sr_location_lat"].between(-90, 90)
    & df["sr_location_long"].between(-180, 180)
)

print("Valid coordinates:", valid_coordinates.sum())
print("Invalid coordinates:", (~valid_coordinates).sum())


print("\n--- TOP 10 REQUEST TYPES ---")
if "sr_type_desc" in df.columns:
    print(df["sr_type_desc"].value_counts().head(10))

print("\n--- SAMPLE RECORDS ---")
print(df.head(5).to_string(index=False))

