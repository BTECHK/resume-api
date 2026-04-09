"""GCP Secret Manager integration with local dev fallback."""

import os
import logging

logger = logging.getLogger(__name__)

_cache: dict[str, str] = {}


def get_secret(secret_id: str, project_id: str | None = None) -> str:
    """Fetch a secret from GCP Secret Manager. Cached after first fetch.

    Requires GCP_PROJECT_ID env var or explicit project_id parameter.
    Cloud Run injects service account credentials automatically.
    """
    if secret_id in _cache:
        return _cache[secret_id]

    project = project_id or os.environ.get("GCP_PROJECT_ID")
    if not project:
        raise RuntimeError("GCP_PROJECT_ID env var not set and no project_id provided")

    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    secret_value = response.payload.data.decode("utf-8")
    _cache[secret_id] = secret_value
    logger.info("Loaded secret: %s", secret_id)
    return secret_value


def get_gemini_key() -> str:
    """Get Gemini API key — from env var (local dev) or Secret Manager (Cloud Run)."""
    if key := os.environ.get("GEMINI_API_KEY"):
        logger.info("Using GEMINI_API_KEY from environment")
        return key
    return get_secret("gemini-api-key")
