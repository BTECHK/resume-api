"""Fixtures for api/ integration tests."""

import sys
import time
from pathlib import Path

import pytest

# Add ai-service/ first so loader.py is importable (same logic as main.py).
_AI_SERVICE_DIR = str(Path(__file__).resolve().parent.parent.parent / "ai-service")
if _AI_SERVICE_DIR not in sys.path:
    sys.path.insert(0, _AI_SERVICE_DIR)

# Add api/ second — it ends up at position 0, so its modules (main, database,
# models, middleware) take priority over ai-service's identically-named files.
_API_DIR = str(Path(__file__).resolve().parent.parent)
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

import database  # noqa: E402


@pytest.fixture(autouse=True)
def _tmp_database(tmp_path, monkeypatch):
    """Redirect database.DATABASE_FILE to a temp SQLite file and init tables."""
    db_file = str(tmp_path / "test_queries.db")
    monkeypatch.setattr(database, "DATABASE_FILE", db_file)
    database.init_db()


@pytest.fixture()
def client():
    """Return a TestClient wired to the FastAPI app."""
    from fastapi.testclient import TestClient
    from main import app

    return TestClient(app)


@pytest.fixture()
def seeded_db():
    """Insert sample rows into the queries table for analytics tests."""
    now = time.time()
    rows = [
        {
            "timestamp": now - 300,
            "method": "GET",
            "path": "/resume",
            "query_params": "",
            "recruiter_domain": "google.com",
            "user_agent": "Mozilla/5.0",
            "client_ip": "1.2.3.4",
            "status_code": 200,
            "response_time_ms": 42.0,
            "session_id": None,
            "search_campaign": None,
            "traffic_source": None,
            "funnel_stage": None,
            "device_type": None,
            "geo_region": None,
        },
        {
            "timestamp": now - 200,
            "method": "GET",
            "path": "/resume/skills",
            "query_params": "",
            "recruiter_domain": "google.com",
            "user_agent": "Mozilla/5.0",
            "client_ip": "5.6.7.8",
            "status_code": 200,
            "response_time_ms": 35.0,
            "session_id": None,
            "search_campaign": None,
            "traffic_source": None,
            "funnel_stage": None,
            "device_type": None,
            "geo_region": None,
        },
        {
            "timestamp": now - 100,
            "method": "GET",
            "path": "/resume/experience",
            "query_params": "",
            "recruiter_domain": "amazon.com",
            "user_agent": "curl/7.68",
            "client_ip": "9.10.11.12",
            "status_code": 200,
            "response_time_ms": 55.0,
            "session_id": None,
            "search_campaign": None,
            "traffic_source": None,
            "funnel_stage": None,
            "device_type": None,
            "geo_region": None,
        },
    ]
    for row in rows:
        database.log_request_to_db(row)
