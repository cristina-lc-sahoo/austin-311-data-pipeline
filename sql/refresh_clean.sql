--This keeps the newest version of each request, based on sr_updated_date
CREATE OR REPLACE TABLE
  `austin-311-data-pipeline.austin_311.service_requests_clean`
AS
SELECT * EXCEPT(row_num)
FROM (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY sr_number
      ORDER BY sr_updated_date DESC
    ) AS row_num
  FROM
    `austin-311-data-pipeline.austin_311.service_requests_raw`
)
WHERE row_num = 1;
