-- File: sql/tier1_naive.sql
-- PURPOSE: Full table scan with no optimization
-- At 500K rows this is fine, but at 500M+ this gets expensive fast

SELECT 
  recruiter_domain, 
  COUNT(*) as total_hits
FROM `resume-api-portfolio.resume_analytics.recruiter_queries`
GROUP BY recruiter_domain
ORDER BY total_hits DESC;

-- RECORD THESE METRICS:
-- Bytes processed: ___________
-- Elapsed time: ___________