--Refresh the monthly summary
CREATE OR REPLACE TABLE
  `austin-311-data-pipeline.austin_311.monthly_request_summary`
AS
SELECT
  DATE_TRUNC(DATE(sr_created_date), MONTH) AS request_month,
  COUNT(*) AS request_count
FROM
  `austin-311-data-pipeline.austin_311.service_requests_clean`
GROUP BY request_month
ORDER BY request_month;
