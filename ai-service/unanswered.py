"""
Unanswered question logger (RAG-07).

Appends a JSONL line for each question the bot cannot confidently answer.
Confidence is derived from the top retrieved chunk's cosine distance:
if the best resume chunk has distance > CONFIDENCE_DISTANCE_THRESHOLD,
the answer is considered weak and the question is logged for future KB improvement.

Log path defaults to /tmp/unanswered_questions.jsonl (Cloud Run ephemeral, visible
through Cloud Logging tail). Override via UNANSWERED_LOG_PATH env var — primarily
for tests.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Distance threshold: cosine distance above this is considered weak match.
# Chroma returns distance in [0, 2] for cosine; lower is better.
CONFIDENCE_DISTANCE_THRESHOLD = 0.7

DEFAULT_LOG_PATH = "/tmp/unanswered_questions.jsonl"

# Question is truncated before logging to avoid storing huge payloads.
MAX_QUESTION_LENGTH = 300


def _get_log_path() -> Path:
    """Read log path from env or fall back to default. Evaluated on every call
    so tests can override mid-run."""
    return Path(os.getenv("UNANSWERED_LOG_PATH", DEFAULT_LOG_PATH))


def is_low_confidence(top_distance: float) -> bool:
    """Return True if the top-result distance indicates a weak match."""
    return top_distance > CONFIDENCE_DISTANCE_THRESHOLD


def log_unanswered(question: str, top_distance: float) -> None:
    """Append a JSONL entry describing a weak/unanswered question.

    Per RAG-07: the question + its top distance + an ISO timestamp are
    written as one line. Does not raise on I/O errors — unanswered logging
    must never break the main request path.
    """
    try:
        log_path = _get_log_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "question": question[:MAX_QUESTION_LENGTH],
            "top_distance": round(float(top_distance), 4),
            "low_confidence": True,
        }
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as exc:
        logger.warning(
            "Failed to write unanswered log | err=%s | path=%s",
            type(exc).__name__, _get_log_path(),
        )


def read_unanswered() -> list[dict]:
    """Read all unanswered entries from the log. Returns empty list if file missing.

    Primarily a convenience helper for tests and offline analysis.
    """
    log_path = _get_log_path()
    if not log_path.exists():
        return []
    entries = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries
