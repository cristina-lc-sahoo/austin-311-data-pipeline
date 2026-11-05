# Austin 311 Data Engineering & Analytics Pipeline

An end-to-end data engineering and analytics project using real Austin 311 service request data. This project demonstrates Python-based data ingestion, Google Cloud Storage, BigQuery transformations, data quality validation, and interactive reporting with Looker Studio.

## Project Overview

The goal is to build a reliable data pipeline that ingests Austin 311 service request data, stores raw source files, transforms and validates records in BigQuery, and presents useful insights through an interactive analytics dashboard.

## Architecture

Python → Google Cloud Storage → BigQuery → Looker Studio

## Technologies

- **Python** — Data ingestion, file processing, and validation
- **Google Cloud Storage** — Raw CSV file storage
- **Google BigQuery** — Cloud data warehouse, SQL transformations, and analytics
- **Looker Studio** — Interactive data visualization and reporting
- **Git / GitHub** — Source control and project documentation

## Work Completed

### 1. Data Ingestion and Processing
- Developed Python scripts to support initial and incremental data ingestion.
- Processed Austin 311 service request CSV files.
- Created batch validation procedures to compare incoming datasets.
- Examined duplicate records across incremental batches.

### 2. Cloud Storage
- Created a Google Cloud project and Cloud Storage bucket.
- Configured a raw incremental storage location.
- Uploaded and verified source CSV files.
- Preserved raw files for auditing and traceability.

### 3. BigQuery Data Warehouse
- Created the `austin_311` dataset.
- Loaded source records into `service_requests_raw`.
- Created `service_requests_clean` using SQL transformations.
- Applied `ROW_NUMBER()` with `PARTITION BY sr_number` and ordering by `sr_updated_date` to retain the latest record for each service request.

### 4. Data Validation and Quality
Validated two incremental batches:

| Validation | Result |
|---|---:|
| First batch records | 25,900 |
| Second batch records | 1,866 |
| Combined raw records | 27,766 |
| Unique service requests | 25,900 |
| Duplicate IDs across batches | 1,866 |
| Duplicate records with differences | 0 |

Additional data quality checks confirmed:
- No missing service request IDs in the clean dataset.
- No missing creation dates.
- No missing statuses.
- Clean record count matched the distinct service request ID count.

### 5. SQL Analytics
Created BigQuery summary tables for reporting:
- `monthly_request_summary` — Monthly service request volume.
- `daily_request_summary_october_2026` — Daily service request volume for October 2026.

Analyzed request trends and used a focused October daily view to make the time-series visualization more meaningful.

### 6. Looker Studio Dashboard
![Austin 311 Service Request Analytics Dashboard](docs/austin-311-dashboard.png)
Created an interactive dashboard titled **Austin 311 Service Request Analytics**, including:
- Total service requests.
- Top 10 service request types.
- Service requests by department.
- Daily service requests for October 2026.

## Current Data Results

- **27,766** raw records loaded.
- **25,900** unique service requests in the clean dataset.
- **0** differences found among the 1,866 repeated records across the two batches.
- Data quality checks completed successfully.

## Repository Contents

- `ingest.py` — Initial data ingestion script.
- `incremental_ingest.py` — Incremental ingestion script.
- `profile_data.py` — Data profiling script.
- `validate_batches.py` — Batch comparison and validation script.
- `data/` — Local source data files (excluded from this public repository).

## Planned Enhancements

The next development phase will focus on automating the pipeline and publishing refreshed analytics:

1. Use GitHub Actions to schedule daily Python ingestion.
2. Retrieve new and updated Austin 311 records.
3. Upload timestamped raw files to Google Cloud Storage.
4. Load and merge records into BigQuery without duplication.
5. Refresh reporting tables and run data quality checks.
6. Configure Looker Studio data freshness.
7. Embed the dashboard in a client-facing website.
8. Add execution logging and failure notifications.

## Project Status

**Current phase:** Initial ingestion, cloud data warehousing, validation, and dashboard development completed.

**Next phase:** Daily pipeline automation and client-facing report publication.

