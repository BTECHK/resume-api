"""
Scale Benchmark 2: Medium Data (500,000 rows)
===============================================
Task: Find the most frequently appearing recruiter domain.
Approach: Python dict/Counter (in-memory), SQLite SQL, BigQuery SQL.

At 500K rows, the Python in-memory approaches still work but consume
meaningful memory and time. SQLite handles it but analytical queries
start to feel heavier. BigQuery handles it effortlessly — this is
what columnar engines are designed for.

This is the crossover point: where the "right tool" question starts
to have a measurable, defensible answer.
"""

import csv
import sqlite3
import time
import tracemalloc
from collections import Counter

# BigQuery client — requires google-cloud-bigquery package
from google.cloud import bigquery

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DB_PATH = "data/analytics.db"
CSV_PATH = "data/recruiter_queries.csv"
SQLITE_TABLE = "recruiter_queries_500k"
BQ_TABLE = "resume-api-portfolio.resume_analytics.recruiter_queries"

def format_bytes(size_bytes):
    """Convert bytes to a human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def print_header():
    print("=" * 70)
    print("  SCALE BENCHMARK 2: MEDIUM DATA (500,000 rows)")
    print("  Task: Find the most frequently appearing recruiter domain")
    print("=" * 70)
    print()

# ---------------------------------------------------------------------------
# Approach 1: Python dict on CSV (in-memory hash map)
# ---------------------------------------------------------------------------
# Same algorithm as benchmark_small.py, but reading 500K rows from CSV.
# Memory usage will climb as we store all domain counts in a dict.
# ---------------------------------------------------------------------------
def benchmark_dict_csv():
    """Load 500K CSV rows into memory, count domains with a dict."""
    tracemalloc.start()
    start = time.perf_counter()

    freq = {}
    row_count = 0
    with open(CSV_PATH, "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        for row in reader:
            domain = row[2]  # recruiter_domain is column index 2
            freq[domain] = freq.get(domain, 0) + 1
            row_count += 1

    top_domain = max(freq, key=freq.get)
    top_count = freq[top_domain]

    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "approach": "Python dict (CSV→memory)",
        "time_sec": elapsed,
        "peak_memory": peak,
        "top_domain": top_domain,
        "top_count": top_count,
        "rows": row_count,
    }

# ---------------------------------------------------------------------------
# Approach 2: Python Counter on CSV
# ---------------------------------------------------------------------------
def benchmark_counter_csv():
    """Load 500K CSV rows, count domains with Counter."""
    tracemalloc.start()
    start = time.perf_counter()

    row_count = 0
    def domain_generator():
        nonlocal row_count
        with open(CSV_PATH, "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                row_count += 1
                yield row[2]  # recruiter_domain

    domain_counts = Counter(domain_generator())
    top_domain, top_count = domain_counts.most_common(1)[0]

    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "approach": "Python Counter (CSV→memory)",
        "time_sec": elapsed,
        "peak_memory": peak,
        "top_domain": top_domain,
        "top_count": top_count,
        "rows": row_count,
    }

# ---------------------------------------------------------------------------
# Approach 3: SQLite GROUP BY on 500K rows
# ---------------------------------------------------------------------------
def benchmark_sqlite_500k():
    """Run GROUP BY on the 500K-row SQLite table."""
    tracemalloc.start()
    start = time.perf_counter()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(f"""
        SELECT recruiter_domain, COUNT(*) as hit_count
        FROM {SQLITE_TABLE}
        GROUP BY recruiter_domain
        ORDER BY hit_count DESC
        LIMIT 1
    """)
    top_domain, top_count = cursor.fetchone()
    conn.close()

    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "approach": "SQLite GROUP BY (500K)",
        "time_sec": elapsed,
        "peak_memory": peak,
        "top_domain": top_domain,
        "top_count": top_count,
        "rows": 500_000,
    }

# ---------------------------------------------------------------------------
# Approach 4: BigQuery GROUP BY (naive — Tier 1 style)
# ---------------------------------------------------------------------------
# BigQuery has 1-3 seconds of job scheduling overhead regardless of data size.
# At 500K rows, the actual scan is fast but the overhead is noticeable.
# The --nouse_cache equivalent in the Python client is:
#   job_config.use_query_cache = False
# This ensures we measure actual scan time, not a cached result.
# ---------------------------------------------------------------------------
def benchmark_bigquery_naive():
    """Run GROUP BY on 500K rows in BigQuery (cache disabled)."""
    start = time.perf_counter()

    client = bigquery.Client()
    job_config = bigquery.QueryJobConfig(use_query_cache=False)

    query = f"""
        SELECT recruiter_domain, COUNT(*) as hit_count
        FROM `{BQ_TABLE}`
        GROUP BY recruiter_domain
        ORDER BY hit_count DESC
        LIMIT 1
    """
    result = client.query(query, job_config=job_config).result()
    row = list(result)[0]
    top_domain = row.recruiter_domain
    top_count = row.hit_count

    elapsed = time.perf_counter() - start

    return {
        "approach": "BigQuery GROUP BY (500K)",
        "time_sec": elapsed,
        "peak_memory": None,  # BigQuery manages its own memory in the cloud
        "top_domain": top_domain,
        "top_count": top_count,
        "rows": 500_000,
    }

# ---------------------------------------------------------------------------
# Approach 5: BigQuery with CTE + Window Functions (Tier 2 style)
# ---------------------------------------------------------------------------
# This shows more advanced SQL — CTEs for readability, RANK() for ranking
# without a subquery, SAFE_DIVIDE for robustness. At 500K rows the
# performance difference vs naive is modest, but the query is more
# production-ready and demonstrates stronger SQL skills.
# ---------------------------------------------------------------------------
def benchmark_bigquery_optimized():
    """Run CTE + window function query on 500K rows in BigQuery."""
    start = time.perf_counter()

    client = bigquery.Client()
    job_config = bigquery.QueryJobConfig(use_query_cache=False)

    query = f"""
        WITH domain_stats AS (
            SELECT
                recruiter_domain,
                COUNT(*) AS total_hits,
                COUNTIF(http_status = 200) AS successful_hits,
                ROUND(AVG(response_time_ms), 2) AS avg_response_ms
            FROM `{BQ_TABLE}`
            GROUP BY recruiter_domain
        ),
        ranked AS (
            SELECT *,
                RANK() OVER (ORDER BY total_hits DESC) AS activity_rank,
                ROUND(SAFE_DIVIDE(successful_hits, total_hits) * 100, 1) AS success_rate_pct
            FROM domain_stats
        )
        SELECT * FROM ranked WHERE activity_rank = 1
    """
    result = client.query(query, job_config=job_config).result()
    row = list(result)[0]
    top_domain = row.recruiter_domain
    top_count = row.total_hits

    elapsed = time.perf_counter() - start

    return {
        "approach": "BigQuery CTE+Window (500K)",
        "time_sec": elapsed,
        "peak_memory": None,
        "top_domain": top_domain,
        "top_count": top_count,
        "rows": 500_000,
    }

# ---------------------------------------------------------------------------
# Run all benchmarks and display results
# ---------------------------------------------------------------------------
def main():
    print_header()

    results = []

    print("  Running Python dict on 500K CSV rows...")
    results.append(benchmark_dict_csv())

    print("  Running Python Counter on 500K CSV rows...")
    results.append(benchmark_counter_csv())

    print("  Running SQLite GROUP BY on 500K rows...")
    results.append(benchmark_sqlite_500k())

    print("  Running BigQuery naive GROUP BY (cache disabled)...")
    results.append(benchmark_bigquery_naive())

    print("  Running BigQuery CTE + Window Functions (cache disabled)...")
    results.append(benchmark_bigquery_optimized())

    print()
    print(f"  {'Approach':<32} {'Time':>10} {'Memory':>10} {'Top Domain':<20} {'Count':>7}")
    print(f"  {'-'*32} {'-'*10} {'-'*10} {'-'*20} {'-'*7}")
    for r in results:
        mem = format_bytes(r["peak_memory"]) if r["peak_memory"] else "cloud"
        print(
            f"  {r['approach']:<32} "
            f"{r['time_sec']:>9.4f}s "
            f"{mem:>10} "
            f"{r['top_domain']:<20} "
            f"{r['top_count']:>7,}"
        )

    print()
    print("  Observations at 500K rows:")
    print("  - Python dict/Counter: still works, but seconds instead of milliseconds")
    print("  - Memory usage: meaningful — the hash map holds all domain counts in RAM")
    print("  - SQLite: handles GROUP BY well (compiled C), but not built for analytics")
    print("  - BigQuery: includes ~1-3s job overhead, but scan itself is fast")
    print("  - BigQuery CTE/Window: similar time, but richer output (ranks, rates)")
    print()
    print("  This is the crossover zone — where the choice of tool starts to")
    print("  have measurable impact on both performance and capability.")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()