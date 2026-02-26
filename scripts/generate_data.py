
import sqlite3
import csv
import random
from faker import Faker
from datetime import datetime, timedelta
import time
import os

# --- Configuration ---
SQLITE_DB_PATH = "data/analytics.db"
CSV_PATH = "data/recruiter_queries.csv"
SQLITE_NUM_ROWS = 10000
CSV_NUM_ROWS = 500000

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

fake = Faker()

# --- Realistic Data Choices ---
RECRUITER_DOMAINS = [
    "google.com", "meta.com", "amazon.com", "deloitte.com", "mckinsey.com",
    "walmart.com", "target.com", "nike.com", "apple.com", "microsoft.com",
    "goldmansachs.com", "jpmorganchase.com", "bcg.com", "bain.com"
]
ENDPOINTS = [
    "/resume", "/resume/experience", "/resume/skills", "/resume/education",
    "/resume/certifications", "/analytics/queries", "/analytics/top-domains"
]
SKILLS = [
    "Python", "SQL", "BigQuery", "API Design", "Cloud", "Agile",
    "Terraform", "AWS", "Docker", "CI/CD", "JavaScript", "React"
]
HTTP_STATUSES = [200, 304, 400, 404, 500]
HTTP_STATUS_WEIGHTS = [85, 5, 4, 4, 2]

# --- Data Generation ---

def create_random_row():
    """Generates a single row of mock analytics data."""
    recruiter_domain = random.choice(RECRUITER_DOMAINS)
    endpoint = random.choice(ENDPOINTS)
    skill = random.choice(SKILLS) if "skills" in endpoint else None

    return (
        fake.date_time_between(start_date="-90d", end_date="now"),
        recruiter_domain,
        endpoint,
        skill,
        random.randint(12, 850),
        random.choices(HTTP_STATUSES, weights=HTTP_STATUS_WEIGHTS, k=1)[0],
        fake.user_agent(),
        f"https://{recruiter_domain}"
    )

def generate_sqlite_data():
    """Generates and populates the SQLite database."""
    print(f"Generating SQLite database with {SQLITE_NUM_ROWS} rows...")
    start_time = time.time()
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS api_queries")
    cursor.execute("""
        CREATE TABLE api_queries (
            query_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            recruiter_domain TEXT,
            endpoint_hit TEXT,
            skill_searched TEXT,
            response_time_ms INTEGER,
            http_status INTEGER,
            user_agent TEXT,
            referer_url TEXT
        )
    """)

    for _ in range(SQLITE_NUM_ROWS):
        cursor.execute("""
            INSERT INTO api_queries (
                timestamp, recruiter_domain, endpoint_hit, skill_searched,
                response_time_ms, http_status, user_agent, referer_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, create_random_row())

    conn.commit()
    conn.close()
    end_time = time.time()
    print(f"SQLite database generated in {end_time - start_time:.2f} seconds.\n")


def generate_csv_data():
    """Generates the large CSV file."""
    print(f"Generating CSV file with {CSV_NUM_ROWS} rows...")
    start_time = time.time()
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        header = [
            "query_id", "timestamp", "recruiter_domain", "endpoint_hit",
            "skill_searched", "response_time_ms", "http_status", "user_agent",
            "referer_url"
        ]
        writer.writerow(header)

        for i in range(CSV_NUM_ROWS):
            row = (i + 1,) + create_random_row()
            writer.writerow(row)
            if (i + 1) % 100000 == 0:
                print(f"  ... {i + 1}/{CSV_NUM_ROWS} rows written")

    end_time = time.time()
    print(f"CSV file generated in {end_time - start_time:.2f} seconds.\n")

if __name__ == "__main__":
    generate_sqlite_data()
    generate_csv_data()
    print("All data generation complete.")
