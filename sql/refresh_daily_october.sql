--Refresh the October daily summary
CREATE OR REPLACE TABLE
  `austin-311-data-pipeline.austin_311.daily_request_summary_october_2026`
AS
SELECT
  DATE(sr_created_date) AS request_date,
  COUNT(*) AS request_count
FROM
  `austin-311-data-pipeline.austin_311.service_requests_clean`
WHERE
  DATE_TRUNC(DATE(sr_created_date), MONTH) = DATE '2026-10-01'
GROUP BY request_date
ORDER BY request_date;
