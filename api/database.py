
import sqlite3
import os

# Use a separate database for live query data
DATABASE_FILE = "data/queries.db"

def get_db_connection():
    """Establishes a connection to the SQLite database for queries."""
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILE)
    # No row_factory needed for simple inserts
    return conn

def init_db():
    """
    Initializes the database and creates the 'queries' table with indexes
    if they don't already exist. This is idempotent and safe to run on startup.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the main queries table for analytics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            query_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            method TEXT NOT NULL DEFAULT 'GET',
            path TEXT NOT NULL,
            query_params TEXT,
            recruiter_domain TEXT DEFAULT 'direct',
            user_agent TEXT,
            client_ip TEXT,
            status_code INTEGER DEFAULT 200,
            response_time_ms REAL,
            synced_to_bq INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            -- Funnel tracking columns (populated by traffic simulator headers)
            session_id TEXT,
            search_campaign TEXT,
            traffic_source TEXT,
            funnel_stage TEXT,
            device_type TEXT,
            geo_region TEXT
        );
    """)

    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_synced ON queries(synced_to_bq);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON queries(timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_domain ON queries(recruiter_domain);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_session ON queries(session_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_campaign ON queries(search_campaign);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_funnel ON queries(funnel_stage);")

    conn.commit()
    conn.close()

def log_request_to_db(data: dict):
    """
    Inserts a single request log entry into the 'queries' table.
    This function is designed to be called from a background task.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # The order of keys in the data dictionary must match the insert statement
    # The 'synced_to_bq' and 'created_at' columns have default values
    cursor.execute("""
        INSERT INTO queries (
            timestamp, method, path, query_params, recruiter_domain,
            user_agent, client_ip, status_code, response_time_ms,
            session_id, search_campaign, traffic_source, funnel_stage,
            device_type, geo_region
        ) VALUES (
            :timestamp, :method, :path, :query_params, :recruiter_domain,
            :user_agent, :client_ip, :status_code, :response_time_ms,
            :session_id, :search_campaign, :traffic_source, :funnel_stage,
            :device_type, :geo_region
        )
    """, data)

    conn.commit()
    conn.close()
