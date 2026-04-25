"""Behavioral tests for main.py endpoints (ai-service).

Covers:
  - Health endpoint warming-up state
  - 503 rejection while service not ready
  - Gemini summarization fallback with warning log
  - Rate-limit handler existence and callability
"""

import logging

import pytest


# ── Test 1: /health returns warming_up before startup ────────────────

def test_health_returns_warming_up_before_startup(test_client, monkeypatch):
    """GET /health returns {"status": "warming_up"} when _startup_ready is False."""
    import main

    monkeypatch.setattr(main, "_startup_ready", False)
    resp = test_client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "warming_up"}


# ── Test 2: /ai/ask and /chat return 503 when not ready ──────────────

def test_warmup_blocked_ask_returns_503(test_client, monkeypatch):
    """POST /ai/ask returns 503 when _startup_ready is False."""
    import main

    monkeypatch.setattr(main, "_startup_ready", False)
    resp = test_client.post("/ai/ask", json={"question": "What skills?"})
    assert resp.status_code == 503
    assert "error" in resp.json()


def test_warmup_blocked_chat_returns_503(test_client, monkeypatch):
    """POST /chat returns 503 when _startup_ready is False."""
    import main

    monkeypatch.setattr(main, "_startup_ready", False)
    resp = test_client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    assert resp.status_code == 503
    assert "error" in resp.json()


# ── Test 3: summarization fallback logs warning ──────────────────────

def test_summarization_fallback_logs_warning(
    test_client, monkeypatch, fake_gemini_client, caplog,
):
    """When >3 chat messages are sent and the Gemini summarization call
    raises, the endpoint should:
      a) still return 200 (truncation fallback)
      b) log a warning about the summarization failure
    """
    import main

    monkeypatch.setattr(main, "_startup_ready", True)

    # Make the FIRST generate_content call (summarization) fail,
    # then let the SECOND call (actual response) succeed.
    call_count = 0
    original_generate = fake_gemini_client.models.generate_content

    def generate_that_fails_first(model, contents):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("Simulated summarization failure")
        return original_generate(model=model, contents=contents)

    fake_gemini_client.models.generate_content = generate_that_fails_first

    # Build 5 messages (> 3 triggers summarization)
    messages = [
        {"role": "user", "content": "What certifications?"},
        {"role": "assistant", "content": "AWS Solutions Architect."},
        {"role": "user", "content": "What about Python?"},
        {"role": "assistant", "content": "8+ years of Python experience."},
        {"role": "user", "content": "Tell me about leadership."},
    ]

    with caplog.at_level(logging.WARNING, logger="main"):
        resp = test_client.post("/chat", json={"messages": messages})

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "answer" in body
    assert body["message_count"] == 5

    # Verify the warning was logged
    warning_messages = [r.message for r in caplog.records if r.levelno == logging.WARNING]
    assert any("summarization failed" in msg.lower() for msg in warning_messages), (
        f"Expected a summarization-failure warning in logs, got: {warning_messages}"
    )


# ── Test 4: rate-limit handler exists and is callable ────────────────

def test_rate_limit_handler_exists_and_callable():
    """Verify _rate_limit_handler is registered and is an async callable."""
    pytest.importorskip("slowapi")
    pytest.importorskip("google.genai")
    pytest.importorskip("chromadb")

    import main
    import asyncio
    import inspect

    handler = main._rate_limit_handler
    assert callable(handler), "_rate_limit_handler must be callable"
    assert inspect.iscoroutinefunction(handler), "_rate_limit_handler must be async"
