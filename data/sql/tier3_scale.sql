-- File: sql/tier3_scale.sql
-- PURPOSE: Create an optimized table structure and show the performance difference
-- This is what you'd recommend to clients processing billions of ad impressions

-- Step 1: Create optimized table
CREATE OR REPLACE TABLE `resume-api-portfolio.resume_analytics.recruiter_queries_optimized`
PARTITION BY DATE(timestamp)
CLUSTER BY recruiter_domain, endpoint_hit
AS SELECT * FROM `resume-api-portfolio.resume_analytics.recruiter_queries`;

-- Step 2: Run a query on the optimized table
-- Dates are calculated dynamically relative to today (see note above if your data doesn't cover recent dates)
SELECT
  recruiter_domain,
  endpoint_hit,
  COUNT(*) AS hits,
  APPROX_QUANTILES(response_time_ms, 100)[OFFSET(95)] AS p95_response_ms,
  APPROX_QUANTILES(response_time_ms, 100)[OFFSET(50)] AS p50_response_ms
FROM `resume-api-portfolio.resume_analytics.recruiter_queries_optimized`
WHERE DATE(timestamp) BETWEEN 
  DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY) AND DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND recruiter_domain IN ('google.com', 'amazon.com')
GROUP BY 1, 2
ORDER BY hits DESC;

-- COMPARE: Bytes scanned on this vs Tier 1
-- Partition pruning + clustering should show dramatic reduction
-- At billions of rows, this is the difference between a $5 query and a $0.05 query

-- WHY PARTITIONING/CLUSTERING MATTERS:
-- Partition by DATE(timestamp): BigQuery skips entire date chunks not in the WHERE clause
-- Cluster by recruiter_domain: Within each partition, data is sorted for efficient filtering
-- APPROX_QUANTILES: BigQuery-native percentile calculations at scale

-- RECORD THESE METRICS:
-- Bytes processed: ___________
-- Elapsed time: ___________
-- Improvement vs Tier 1: ___________%