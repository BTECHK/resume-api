-- File: sql/tier2_optimized.sql
-- PURPOSE: Production-quality query using CTE, window functions, SAFE_DIVIDE
-- Mirrors the SQL patterns used in ad tech reporting

WITH recruiter_stats AS (
  SELECT
    recruiter_domain,
    COUNT(*) AS total_hits,
    COUNTIF(http_status = 200) AS successful_hits,
    ROUND(AVG(response_time_ms), 2) AS avg_response_ms,
    APPROX_TOP_COUNT(skill_searched, 1)[OFFSET(0)].value AS top_skill_searched,
    MIN(timestamp) AS first_visit,
    MAX(timestamp) AS last_visit
  FROM `resume-api-portfolio.resume_analytics.recruiter_queries`
  WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
  GROUP BY recruiter_domain
),

ranked AS (
  SELECT
    *,
    RANK() OVER (ORDER BY total_hits DESC) AS activity_rank,
    ROUND(SAFE_DIVIDE(successful_hits, total_hits) * 100, 1) AS success_rate_pct,
    DATE_DIFF(DATE(last_visit), DATE(first_visit), DAY) AS engagement_span_days
  FROM recruiter_stats
)

SELECT * FROM ranked
WHERE activity_rank <= 10
ORDER BY activity_rank;

-- WHAT THIS DEMONSTRATES:
-- CTE: Readable, maintainable multi-step logic
-- COUNTIF: Conditional aggregation (ads data has zeroes everywhere)
-- APPROX_TOP_COUNT: BigQuery-specific approximate function
-- RANK() OVER: Window function for ranking without self-join
-- SAFE_DIVIDE: Prevents division by zero
-- DATE_DIFF: Date arithmetic
-- TIMESTAMP_SUB: Partition-friendly date filtering

-- RECORD THESE METRICS:
-- Bytes processed: ___________
-- Elapsed time: ___________
-- Improvement vs Tier 1: ___________%