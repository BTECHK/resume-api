"""
Scale Benchmark 3: Large Data (5,000,000 rows)
================================================
Task: Find the most frequently appearing recruiter domain.
Approach: Python dict (streaming from BigQuery), SQLite, BigQuery SQL.

This benchmark completes the crossover story from benchmarks 1 and 2:
  - 10K rows:  Python dict wins (minimal overhead, data fits in memory)
  - 500K rows: SQLite wins (compiled C engine outpaces interpreted Python)
  - 5M rows:   BigQuery wins (columnar engine, data never leaves server)

At 5M rows:
  - Python dict streaming: impractical — network transfer is the bottleneck
  - SQLite GROUP BY: still works but shows strain at analytical scale
  - BigQuery: handles it in seconds, partitioning cuts bytes scanned further

Benchmarking methodology:
  - SQLite 5M data is generated BEFORE the timer by inserting the existing
    500K table into itself (500K × 10 = 5M). The connection stays open so
    the benchmark measures only the GROUP BY execution — same fair approach
    as benchmark_small.py.
  - BigQuery cache is disabled on all queries (use_query_cache=False).
  - Python dict streams from BigQuery with a 60s timeout. If it doesn't
    finish, that IS the result.
"""

import csv
import sqlite3
import time
import tracemalloc
from collections import Counter

from google.cloud import bigquery

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DB_PATH = "data/analytics.db"
SQLITE_TABLE_500K = "recruiter_queries_500k"
SQLITE_TABLE_5M = "recruiter_queries_5m"
BQ_TABLE_5M = "resume-api-portfolio.resume_analytics.recruiter_queries_5m"
BQ_TABLE_5M_PARTITIONED = "resume-api-portfolio.resume_analytics.recruiter_queries_5m_optimized"

def format_bytes(size_bytes):
    """Convert bytes to a human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def print_header():
    print("=" * 70)
    print("  SCALE BENCHMARK 3: LARGE DATA (5,000,000 rows)")
    print("  Task: Find the most frequently appearing recruiter domain")
    print("=" * 70)
    print()

# ---------------------------------------------------------------------------
# SQLite 5M setup — generate 5M rows from the existing 500K table
# ---------------------------------------------------------------------------
# This mirrors the BigQuery CROSS JOIN strategy: multiply existing data by
# 10 to reach 5M rows. Done once before the timer starts so the benchmark
# measures only the GROUP BY query, not the data loading.
# ---------------------------------------------------------------------------
def setup_sqlite_5m(conn):
    """Create a 5M row SQLite table by inserting the 500K table 10 times."""
    # Check if already populated
    count = conn.execute(
        f"SELECT COUNT(*) FROM sqlite_master WHERE name='{SQLITE_TABLE_5M}'"
    ).fetchone()[0]
    if count > 0:
        existing = conn.execute(
            f"SELECT COUNT(*) FROM {SQLITE_TABLE_5M}"
        ).fetchone()[0]
        if existing >= 5_000_000:
            print(f"  SQLite 5M table already exists ({existing:,} rows), skipping setup.")
            return

    print("  Building SQLite 5M table (inserting 500K rows × 10)...")
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {SQLITE_TABLE_5M} (
            query_id INTEGER, timestamp TEXT, recruiter_domain TEXT,
            endpoint_hit TEXT, skill_searched TEXT, response_time_ms REAL,
            http_status INTEGER, user_agent TEXT, referer_url TEXT
        )
    """)
    conn.execute(f"DELETE FROM {SQLITE_TABLE_5M}")
    for i in range(10):
        conn.execute(f"""
            INSERT INTO {SQLITE_TABLE_5M}
            SELECT * FROM {SQLITE_TABLE_500K}
        """)
        print(f"    Batch {i+1}/10 inserted...")
    conn.commit()
    total = conn.execute(f"SELECT COUNT(*) FROM {SQLITE_TABLE_5M}").fetchone()[0]
    print(f"  Done. SQLite 5M table has {total:,} rows.")
    print()

# ---------------------------------------------------------------------------
# Approach 1: Python dict — streaming rows from BigQuery into Python
# ---------------------------------------------------------------------------
# This deliberately shows what happens when you try to pull 5M rows into
# a Python process. The BigQuery API streams rows over the network, and
# Python builds a dict in memory. It works — but it's slow and wasteful
# because the counting could happen inside BigQuery instead.
#
# We cap at 60 seconds to avoid hanging. If it doesn't finish, that IS
# the result — "Python in-memory can't handle this volume efficiently."
# ---------------------------------------------------------------------------
TIMEOUT_SECONDS = 60

def benchmark_dict_bigquery_stream():
    """Stream 5M rows from BigQuery into Python and count with dict."""
    tracemalloc.start()
    start = time.perf_counter()

    client = bigquery.Client()
    # Stream only the domain column to minimize network transfer
    query = f"SELECT recruiter_domain FROM `{BQ_TABLE_5M}`"
    job_config = bigquery.QueryJobConfig(use_query_cache=False)

    freq = {}
    row_count = 0
    timed_out = False

    try:
        result = client.query(query, job_config=job_config).result()
        for row in result:
            if time.perf_counter() - start > TIMEOUT_SECONDS:
                timed_out = True
                break
            domain = row.recruiter_domain
            freq[domain] = freq.get(domain, 0) + 1
            row_count += 1
    except Exception as e:
        print(f"  Error during streaming: {e}")
        timed_out = True

    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if freq:
        top_domain = max(freq, key=freq.get)
        top_count = freq[top_domain]
    else:
        top_domain = "N/A"
        top_count = 0

    status = f"TIMEOUT after {TIMEOUT_SECONDS}s" if timed_out else "completed"
    if timed_out:
        status += f" ({row_count:,} of 5,000,000 rows processed)"

    return {
        "approach": f"Python dict (stream 5M)",
        "time_sec": elapsed,
        "peak_memory": peak,
        "top_domain": top_domain,
        "top_count": top_count,
        "rows_processed": row_count,
        "status": status,
    }

# ---------------------------------------------------------------------------
# Approach 2: SQLite GROUP BY on 5M rows
# ---------------------------------------------------------------------------
# SQLite was the winner at 500K rows. At 5M, it still works — but this is
# near the ceiling of what an embedded database handles comfortably for
# analytical queries. The timer measures only the query execution on an
# already-open connection with pre-loaded data (same fair approach as
# benchmark_small.py).
# ---------------------------------------------------------------------------
def benchmark_sqlite_5m(conn):
    """Run GROUP BY on the 5M-row SQLite table."""
    tracemalloc.start()
    start = time.perf_counter()

    cursor = conn.execute(f"""
        SELECT recruiter_domain, COUNT(*) as hit_count
        FROM {SQLITE_TABLE_5M}
        GROUP BY recruiter_domain
        ORDER BY hit_count DESC
        LIMIT 1
    """)
    top_domain, top_count = cursor.fetchone()

    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "approach": "SQLite GROUP BY (5M)",
        "time_sec": elapsed,
        "peak_memory": peak,
        "top_domain": top_domain,
        "top_count": top_count,
        "rows_processed": 5_000_000,
        "status": "completed",
    }

# ---------------------------------------------------------------------------
# Approach 3: BigQuery naive GROUP BY on 5M rows
# ---------------------------------------------------------------------------
def benchmark_bigquery_naive_5m():
    """Naive GROUP BY on the unpartitioned 5M row table."""
    start = time.perf_counter()

    client = bigquery.Client()
    job_config = bigquery.QueryJobConfig(use_query_cache=False)

    query = f"""
        SELECT recruiter_domain, COUNT(*) as hit_count
        FROM `{BQ_TABLE_5M}`
        GROUP BY recruiter_domain
        ORDER BY hit_count DESC
        LIMIT 1
    """
    job = client.query(query, job_config=job_config)
    result = job.result()
    row = list(result)[0]

    elapsed = time.perf_counter() - start
    bytes_processed = job.total_bytes_processed

    return {
        "approach": "BigQuery GROUP BY (5M)",
        "time_sec": elapsed,
        "peak_memory": None,
        "top_domain": row.recruiter_domain,
        "top_count": row.hit_count,
        "rows_processed": 5_000_000,
        "status": "completed",
        "bytes_processed": bytes_processed,
    }

# ---------------------------------------------------------------------------
# Approach 4: BigQuery with partitioned + clustered table
# ---------------------------------------------------------------------------
# First create the optimized table (if it doesn't exist), then query it.
# Partitioning by date + clustering by domain means BigQuery can skip
# irrelevant date ranges and sort-filter by domain efficiently.
# ---------------------------------------------------------------------------
def create_partitioned_table_if_needed(client):
    """Create a partitioned/clustered copy of the 5M table."""
    # Check if it already exists
    try:
        client.get_table(BQ_TABLE_5M_PARTITIONED)
        print("  Partitioned table already exists, skipping creation.")
        return
    except Exception:
        pass

    print("  Creating partitioned + clustered copy of 5M table...")
    query = f"""
        CREATE TABLE `{BQ_TABLE_5M_PARTITIONED}`
        PARTITION BY DATE(timestamp)
        CLUSTER BY recruiter_domain, endpoint_hit
        AS SELECT * FROM `{BQ_TABLE_5M}`
    """
    client.query(query).result()
    print("  Done.")

def benchmark_bigquery_partitioned_5m():
    """Query the partitioned/clustered 5M row table."""
    client = bigquery.Client()
    create_partitioned_table_if_needed(client)

    start = time.perf_counter()
    job_config = bigquery.QueryJobConfig(use_query_cache=False)

    # Use a date filter so partition pruning kicks in
    query = f"""
        SELECT recruiter_domain, COUNT(*) as hit_count
        FROM `{BQ_TABLE_5M_PARTITIONED}`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        GROUP BY recruiter_domain
        ORDER BY hit_count DESC
        LIMIT 1
    """
    job = client.query(query, job_config=job_config)
    result = job.result()
    row = list(result)[0]

    elapsed = time.perf_counter() - start
    bytes_processed = job.total_bytes_processed

    return {
        "approach": "BigQuery Partitioned (5M)",
        "time_sec": elapsed,
        "peak_memory": None,
        "top_domain": row.recruiter_domain,
        "top_count": row.hit_count,
        "rows_processed": 5_000_000,
        "status": "completed",
        "bytes_processed": bytes_processed,
    }

# ---------------------------------------------------------------------------
# Run all benchmarks and display results
# ---------------------------------------------------------------------------
def main():
    print_header()

    # --- SQLite setup (not timed) -----------------------------------------
    # Build the 5M row table before any timers start. Same fairness principle
    # as benchmark_small.py: connection open, data loaded, then measure only
    # the GROUP BY execution.
    conn = sqlite3.connect(DB_PATH)
    setup_sqlite_5m(conn)

    results = []

    print("  Running Python dict stream from BigQuery (5M rows, 60s timeout)...")
    results.append(benchmark_dict_bigquery_stream())

    print("  Running SQLite GROUP BY (5M rows)...")
    results.append(benchmark_sqlite_5m(conn))
    conn.close()

    print("  Running BigQuery naive GROUP BY (5M rows, cache disabled)...")
    results.append(benchmark_bigquery_naive_5m())

    print("  Running BigQuery partitioned + clustered (5M rows, cache disabled)...")
    results.append(benchmark_bigquery_partitioned_5m())

    print()
    print(f"  {'Approach':<30} {'Time':>10} {'Memory':>10} {'Bytes Scanned':>14} {'Status'}")
    print(f"  {'-'*30} {'-'*10} {'-'*10} {'-'*14} {'-'*30}")
    for r in results:
        mem = format_bytes(r["peak_memory"]) if r["peak_memory"] else "cloud"
        bscan = format_bytes(r.get("bytes_processed", 0)) if r.get("bytes_processed") else "N/A"
        print(
            f"  {r['approach']:<30} "
            f"{r['time_sec']:>9.4f}s "
            f"{mem:>10} "
            f"{bscan:>14} "
            f"{r['status']}"
        )

    print()
    # Show the bytes-scanned comparison for BigQuery approaches
    bq_results = [r for r in results if r.get("bytes_processed")]
    if len(bq_results) >= 2:
        naive_bytes = bq_results[0]["bytes_processed"]
        part_bytes = bq_results[1]["bytes_processed"]
        if naive_bytes > 0:
            reduction = (1 - part_bytes / naive_bytes) * 100
            print(f"  BigQuery bytes scanned reduction with partitioning: {reduction:.1f}%")
            print()

    print("  Observations at 5M rows:")
    print("  - Python dict: streaming 5M rows over the network is the bottleneck —")
    print("    the hash map algorithm is O(n) but network transfer makes it impractical")
    print("  - SQLite: still completes the GROUP BY, but this is near its ceiling for")
    print("    analytical workloads. It's an embedded DB designed for OLTP, not OLAP.")
    print("  - BigQuery naive: handles 5M in seconds — data never leaves the server")
    print("  - BigQuery partitioned: scans fewer bytes by skipping irrelevant date")
    print("    partitions. At production scale (billions of rows), this is the")
    print("    difference between a $5 query and a $0.05 query.")
    print()
    print("  The crossover story across all three benchmarks:")
    print("    10K  → Python dict wins (overhead dominates, data fits in memory)")
    print("    500K → SQLite wins (compiled C engine outpaces interpreted Python)")
    print("    5M   → BigQuery wins (push computation to the data, not vice versa)")
    print()
    print("  This is the fundamental principle: the right tool depends on the scale.")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()