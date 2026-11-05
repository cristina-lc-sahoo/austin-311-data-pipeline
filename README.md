# Austin 311 Data Engineering & Analytics Pipeline

An end-to-end cloud data engineering project that ingests, stores, transforms, validates, and visualizes real Austin 311 service request data. The pipeline uses Python and Google Cloud services to automate incremental data ingestion and refresh analytical reporting tables.

## Project Overview

This project demonstrates the development of a cloud-based data pipeline, from public API ingestion through data warehousing and business intelligence reporting.

The solution retrieves new and updated Austin 311 service requests, stores timestamped raw data files in Google Cloud Storage, loads records into BigQuery, applies SQL transformations, and provides interactive analytics through Looker Studio.

The pipeline is containerized and deployed as a Cloud Run Job, with Cloud Scheduler configured to trigger daily execution.

## Architecture

**End-to-end pipeline:**

Austin 311 Public API → Cloud Run Job (Python) → Google Cloud Storage → BigQuery → Looker Studio → Google Sites

### Google Cloud Components

- **Cloud Scheduler** — Triggers the pipeline daily at 6:00 AM Central Time.
- **Cloud Run Jobs** — Executes the containerized Python ingestion and orchestration process.
- **Artifact Registry** — Stores the Docker container image.
- **Google Cloud Storage** — Stores timestamped incremental CSV files, SQL transformation scripts, and the pipeline watermark.
- **BigQuery** — Stores raw and cleaned service request data and analytical summary tables.
- **Looker Studio** — Provides interactive dashboards and visual analytics.
- **Google Sites** — Hosts the published, client-facing analytics website.

## Pipeline Implementation

### 1. API Ingestion and Incremental Processing

- Developed Python scripts to retrieve Austin 311 service request data from the public API.
- Implemented initial and incremental ingestion.
- Uses a stored pipeline watermark to identify the starting point for subsequent runs.
- Applies a 48-hour overlap to capture newly created and updated service requests.
- Retrieves records in paginated batches.
- Generates timestamped CSV files for traceability.

### 2. Cloud Storage

- Created and configured a Google Cloud Storage bucket.
- Uploads incremental CSV files to a raw storage location.
- Stores SQL transformation scripts separately from the container image.
- Maintains the last successful run timestamp in a pipeline state file.

### 3. BigQuery Data Warehouse

Created the `austin_311` dataset with the following tables:

- `service_requests_raw` — Appended source records from incremental ingestion.
- `service_requests_clean` — Deduplicated service requests, retaining the latest available version.
- `monthly_request_summary` — Monthly service request counts.
- `daily_request_summary_october_2026` — Daily service request counts for October 2026.

### 4. SQL Transformations

Python handles pipeline orchestration, while SQL performs data transformations directly in BigQuery.

The pipeline executes three SQL scripts:

- `refresh_clean.sql` — Uses `ROW_NUMBER()` partitioned by service request number and ordered by update timestamp to retain the latest record.
- `refresh_monthly.sql` — Rebuilds monthly service request summaries.
- `refresh_daily_october.sql` — Rebuilds daily service request summaries for October 2026.

Summary tables are rebuilt after incoming records are loaded successfully.

### 5. Data Quality and Validation

Validated incremental ingestion through batch comparison and BigQuery data quality checks.

**Initial batch validation:**

| Validation | Result |
|---|---:|
| First batch records | 25,900 |
| Second batch records | 1,866 |
| Combined raw records | 27,766 |
| Unique service requests | 25,900 |
| Repeated IDs across batches | 1,866 |
| Repeated records with differences | 0 |

Additional BigQuery validation confirmed:

- No missing service request IDs in the clean dataset.
- No missing creation dates.
- No missing statuses.
- One clean record per distinct service request ID.

### 6. Pipeline Automation

Containerized the Python pipeline using Docker and deployed it as a Google Cloud Run Job.

Configured Cloud Scheduler to invoke the job daily at 6:00 AM Central Time.

The automated workflow:

1. Retrieves the last successful run timestamp from Cloud Storage.
2. Requests new and updated records from the Austin 311 API using a 48-hour overlap.
3. Creates and uploads a timestamped CSV file to Google Cloud Storage.
4. Appends incoming records to the BigQuery raw table.
5. Executes SQL transformations to rebuild the clean and summary tables.
6. Updates the pipeline watermark after successful processing.

The watermark is updated only after the data load and SQL transformations complete successfully.

### 7. Analytics and Reporting

Created an interactive Looker Studio dashboard titled **Austin 311 Service Request Analytics**.

Dashboard includes:

- Total service requests.
- Top 10 service request types.
- Service requests by department.
- Daily service requests for October 2026.
- Monthly service request trends.

**Project links:**

- [View the Looker Studio Dashboard](https://datastudio.google.com/reporting/57ca4424-9ab4-4b5c-9cdb-7e8d1c475f9c)
- [View the Published Google Sites Website](https://sites.google.com/view/austin-311-analytics/)
- [Dashboard Screenshot](https://github.com/cristina-lc-sahoo/austin-311-data-pipeline/blob/main/docs/austin-311-dashboard.png)

## Latest Pipeline Results

Latest successful manual Cloud Run execution (November 5, 2026):

| BigQuery Table | Row Count |
|---|---:|
| `service_requests_raw` | 29,728 |
| `service_requests_clean` | 26,816 |
| `monthly_request_summary` | 37 |
| `daily_request_summary_october_2026` | 31 |

The clean table was independently validated for duplicate service request IDs and missing required fields.

## Technologies

- **Languages:** Python, SQL
- **Cloud Platform:** Google Cloud Platform (GCP)
- **Data Storage:** Google Cloud Storage
- **Data Warehouse:** Google BigQuery
- **Orchestration:** Cloud Scheduler, Cloud Run Jobs
- **Containerization:** Docker
- **Container Registry:** Artifact Registry
- **Analytics & Reporting:** Looker Studio, Google Sites
- **Version Control:** Git, GitHub

## Repository Contents

- `ingest.py` — Initial data ingestion script.
- `incremental_ingest.py` — Incremental API ingestion script.
- `profile_data.py` — Source data profiling and inspection.
- `validate_batches.py` — Batch comparison and validation.
- `daily_pipeline.py` — Automated pipeline orchestration, GCS integration, BigQuery loading, and SQL execution.
- `Dockerfile` — Defines the container image used by Cloud Run.
- `requirements.txt` — Python dependencies.
- `sql/refresh_clean.sql` — Clean table transformation.
- `sql/refresh_monthly.sql` — Monthly summary transformation.
- `sql/refresh_daily_october.sql` — October daily summary transformation.
- `data/` — Local source data files, excluded from the public repository.

## Project Status and Future Improvements

**Completed:**

- Initial and incremental API ingestion.
- Source profiling and batch validation.
- Google Cloud Storage integration.
- BigQuery raw and clean data processing.
- SQL-based transformations and summary tables.
- Docker containerization and Cloud Run Job deployment.
- Cloud Scheduler daily schedule configuration.
- Successful manual end-to-end pipeline execution.
- Looker Studio dashboard development.
- Dashboard publication through Google Sites.
- GitHub project documentation and source control.

**Next improvements:**

- Verify the first scheduled daily execution.
- Improve raw-table idempotency to prevent duplicate appends during retries.
- Make the October-specific daily summary dynamic.
- Add pipeline monitoring, execution logging, and failure notifications.
- Expand analytical reporting and dashboard capabilities.


