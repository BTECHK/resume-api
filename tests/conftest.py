"""Shared pytest fixtures for Resume API tests."""

import pytest


@pytest.fixture
def api_base_url():
    """Base URL for the API under test."""
    return "http://localhost:8000"
