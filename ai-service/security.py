"""
Security middleware for the AI service.

Provides:
- Prompt injection detection (regex-based, per D-03/D-04/D-05)
- IP flagging with time-based cooldown for dynamic rate reduction
- Response sanitization to scrub PII from Gemini output (per D-08/D-10)
- Safe error response helper that never leaks internals (SEC-07)
"""

import re
import time
import logging
from collections import defaultdict
from pathlib import Path

import yaml
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# Prompt Injection Detection (SEC-02, D-03, D-04, D-05)
# ──────────────────────────────────────────────────────────────

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions?",
    r"system\s*prompt",
    r"you\s+are\s+now\s+",
    r"pretend\s+(you\s+are|to\s+be)",
    r"jailbreak",
    r"DAN\s+mode",
    r"act\s+as\s+(if\s+you\s+are|a\s+)",
    r"disregard\s+(all|your|previous)",
    r"\[INST\]|\[SYS\]|<\|im_start\|>",
    r"reveal\s+(your|the)\s+(system|hidden|secret)",
    r"what\s+are\s+your\s+instructions",
    r"repeat\s+(the\s+)?(above|previous)\s+(text|instructions|prompt)",
]

_compiled_patterns = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

# ──────────────────────────────────────────────────────────────
# IP Flagging for Dynamic Rate Reduction (D-04)
# ──────────────────────────────────────────────────────────────

# Stores {ip: (flag_timestamp, flag_count)}
_flagged_ips: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))
FLAG_DURATION_SECONDS = 300  # 5 minutes per D-04 (research recommended 15 min, 5 is reasonable)


def check_injection(text: str) -> str | None:
    """Check text for prompt injection patterns.

    Returns the matched pattern string if injection detected, else None.
    Per D-05: logs the detected pattern name, NOT the full malicious payload.
    """
    for pattern in _compiled_patterns:
        match = pattern.search(text)
        if match:
            return match.group(0)
    return None


def flag_ip(ip: str) -> None:
    """Mark an IP as flagged for injection attempt. Increments flag count.

    Per D-04: flagged IPs get reduced rate limits (handled by main.py).
    Per D-05: logs IP and timestamp but NOT the full payload.
    """
    _timestamp, count = _flagged_ips[ip]
    _flagged_ips[ip] = (time.time(), count + 1)
    logger.warning(
        "Injection attempt flagged | ip=%s | count=%d | window=%ds",
        ip, count + 1, FLAG_DURATION_SECONDS
    )


def is_flagged(ip: str) -> bool:
    """Check if an IP is currently under rate reduction.

    Returns True if the IP was flagged within the last FLAG_DURATION_SECONDS.
    """
    flag_time, count = _flagged_ips.get(ip, (0.0, 0))
    if count == 0:
        return False
    if (time.time() - flag_time) < FLAG_DURATION_SECONDS:
        return True
    # Expired — clean up
    del _flagged_ips[ip]
    return False


# ──────────────────────────────────────────────────────────────
# Response Sanitization (SEC-09, D-08, D-10)
# Patterns reimplemented independently — belt-and-suspenders defense
# ──────────────────────────────────────────────────────────────

_PATTERNS_FILE = Path(__file__).parent / "scrub_patterns.yaml"
_EXAMPLE_FILE = Path(__file__).parent / "scrub_patterns.example.yaml"


def _load_name_scrub_patterns() -> list[tuple[re.Pattern, str]]:
    try:
        f = _PATTERNS_FILE if _PATTERNS_FILE.exists() else _EXAMPLE_FILE
        raw = yaml.safe_load(f.read_text()) or {}
        return [(re.compile(p, re.IGNORECASE), r) for p, r in raw.items()]
    except Exception as exc:
        logger.warning("Failed to load scrub patterns from %s: %s", f, type(exc).__name__, exc_info=True)
        return []


RESPONSE_SCRUB_PATTERNS = [
    *_load_name_scrub_patterns(),
    (re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"), "[email redacted]"),
    (re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[phone redacted]"),
    (re.compile(r"https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?"), "[linkedin redacted]"),
    (re.compile(r"\b\d+\s+[A-Z][a-z]+\s+(?:St|Ave|Blvd|Dr|Rd|Ln|Way|Ct)\b"), "[address redacted]"),
]


def sanitize_response(text: str) -> str:
    """Scrub PII from Gemini output before returning to client.

    This is the runtime defense layer (D-10). Even if prompts.py and
    resume_data.py are properly anonymized (build-time defense), Gemini
    might hallucinate real names or details. This catches those.
    """
    for pattern, replacement in RESPONSE_SCRUB_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


# ──────────────────────────────────────────────────────────────
# Safe Error Responses (SEC-07)
# ──────────────────────────────────────────────────────────────

def safe_error_response(status_code: int = 500, detail: str = "An error occurred") -> JSONResponse:
    """Return a generic error response that never leaks internal details.

    Per SEC-07: stack traces, model names, file paths, and configuration
    details must never appear in error responses to clients.
    """
    # Map status codes to safe messages
    safe_messages = {
        400: "Invalid request",
        422: "Invalid input — please check your question format",
        429: "Too many requests — please try again later",
        500: "The AI service encountered an error — please try again",
        503: "The AI service is temporarily unavailable",
    }
    message = safe_messages.get(status_code, detail)
    return JSONResponse(
        status_code=status_code,
        content={"error": message},
    )
