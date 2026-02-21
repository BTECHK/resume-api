-- Generate a 5M row table by cross-joining the existing 500K table with a 10-element array.
-- CROSS JOIN produces a Cartesian product: every row paired with every array element.
-- 500,000 rows × 10 = 5,000,000 rows. The data stays inside BigQuery — nothing is uploaded.

CREATE TABLE `resume-api-portfolio.resume_analytics.recruiter_queries_5m` AS
SELECT
  -- ROW_NUMBER generates new unique IDs so the 5M table doesn't have duplicate query_ids
  ROW_NUMBER() OVER() AS query_id,
  a.timestamp,
  a.recruiter_domain,
  a.endpoint_hit,
  a.skill_searched,
  a.response_time_ms,
  a.http_status,
  a.user_agent,
  a.referer_url
FROM `resume-api-portfolio.resume_analytics.recruiter_queries` a
CROSS JOIN UNNEST(GENERATE_ARRAY(1, 10)) AS multiplier;