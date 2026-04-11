"""Integration tests for /health, /ai/ask, /chat endpoints — TEST-02 coverage.

Uses FastAPI TestClient with a fake RAG and fake Gemini client so the tests
exercise the real request pipeline (validation, injection check, retrieval,
generation, sanitization) without hitting external services or loading heavy
ML models. Skips automatically when slowapi/google-genai/chromadb aren't
installed locally; CI runs them against the full requirements.
"""

import json


def test_health_endpoint_reports_ok(test_client):
    """GET /health should return ok + index_size + model name."""
    response = test_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model"] == "gemini-2.5-flash"
    assert isinstance(body["index_size"], int)


def test_ask_factual_question_returns_answer(test_client, fake_gemini_client):
    """Factual question should invoke Gemini and return AskResponse shape."""
    fake_gemini_client.models._canned = "The candidate holds AWS Solutions Architect certification."
    response = test_client.post("/ai/ask", json={"question": "What certifications?"})
    assert response.status_code == 200
    body = response.json()
    assert "AWS" in body["answer"]
    assert isinstance(body["sources"], list)
    assert len(body["sources"]) == 3
    assert body["model_used"] == "gemini-2.5-flash"
    assert "chunk" in body["sources"][0]
    assert "relevance" in body["sources"][0]


def test_ask_behavioral_question_triggers_interview_tier(test_client, fake_gemini_client, fake_rag):
    """A leadership question should pull tier-2 interview patterns into the prompt."""
    response = test_client.post(
        "/ai/ask",
        json={"question": "Tell me about a time you showed leadership in a conflict"},
    )
    assert response.status_code == 200
    # Verify the fake RAG got the query and interview chunks were included in the prompt
    assert fake_rag.last_query is not None
    last_prompt = fake_gemini_client.models.calls[-1]["contents"]
    assert "INTERVIEW PATTERNS" in last_prompt
    assert "leadership" in last_prompt.lower()


def test_ask_architecture_question_triggers_arch_tier(test_client, fake_gemini_client):
    """An architecture question should pull ADR content into the prompt."""
    response = test_client.post(
        "/ai/ask",
        json={"question": "What is the tech stack and embedding model?"},
    )
    assert response.status_code == 200
    last_prompt = fake_gemini_client.models.calls[-1]["contents"]
    assert "SYSTEM ARCHITECTURE" in last_prompt
    assert "Gemini" in last_prompt


def test_ask_empty_question_rejected(test_client):
    """Empty question should fail Pydantic validation (422)."""
    response = test_client.post("/ai/ask", json={"question": "   "})
    assert response.status_code == 422


def test_ask_long_question_rejected(test_client):
    """Question over 500 chars should fail Pydantic validation (422)."""
    too_long = "What " + ("skills " * 120)
    response = test_client.post("/ai/ask", json={"question": too_long})
    assert response.status_code == 422


def test_ask_low_confidence_logs_unanswered(test_client, tmp_path, monkeypatch):
    """A question that produces a high retrieval distance should be logged."""
    log_path = tmp_path / "unanswered.jsonl"
    monkeypatch.setenv("UNANSWERED_LOG_PATH", str(log_path))
    response = test_client.post(
        "/ai/ask",
        json={"question": "What color is the candidate's bugatti?"},
    )
    assert response.status_code == 200
    # The unanswered logger should have written a JSONL line
    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= 1
    entry = json.loads(lines[-1])
    assert entry["low_confidence"] is True
    assert "bugatti" in entry["question"].lower()


def test_ask_gemini_failure_returns_503(test_client, fake_gemini_client):
    """If Gemini raises, the endpoint returns 503 with a safe error."""
    def _boom(*args, **kwargs):
        raise RuntimeError("simulated gemini failure")
    fake_gemini_client.models.generate_content = _boom
    response = test_client.post("/ai/ask", json={"question": "What certifications?"})
    assert response.status_code == 503
    body = response.json()
    assert "error" in body


def test_chat_single_message_works(test_client, fake_gemini_client):
    """Single-message /chat should return ChatResponse with message_count=1."""
    fake_gemini_client.models._canned = "Here is the mocked chat answer."
    response = test_client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "Hi, tell me about the candidate"}]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["message_count"] == 1
    assert "mocked chat" in body["answer"]
    assert body["model_used"] == "gemini-2.5-flash"
    assert len(body["sources"]) == 3


def test_chat_requires_last_message_user(test_client):
    """A trailing assistant message should fail validation (422)."""
    response = test_client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Hello"},
            ],
        },
    )
    assert response.status_code == 422


def test_chat_empty_messages_rejected(test_client):
    """Empty messages list should fail validation."""
    response = test_client.post("/chat", json={"messages": []})
    assert response.status_code == 422


def test_chat_exceeds_10_messages_rejected(test_client):
    """More than 10 messages should fail validation (D-06)."""
    messages = []
    for i in range(11):
        messages.append({"role": "user" if i % 2 == 0 else "assistant", "content": f"msg {i}"})
    messages[-1]["role"] = "user"
    response = test_client.post("/chat", json={"messages": messages})
    assert response.status_code == 422


def test_chat_with_history_triggers_summarization(test_client, fake_gemini_client):
    """More than 3 messages should invoke an extra Gemini call for summarization (D-07)."""
    fake_gemini_client.models._canned = "Summary + answer."
    messages = [
        {"role": "user", "content": "Q1"},
        {"role": "assistant", "content": "A1"},
        {"role": "user", "content": "Q2"},
        {"role": "assistant", "content": "A2"},
        {"role": "user", "content": "Latest question"},
    ]
    response = test_client.post("/chat", json={"messages": messages})
    assert response.status_code == 200
    # Expect at least 2 Gemini calls: summarization + final answer
    assert len(fake_gemini_client.models.calls) >= 2


def test_chat_last_message_too_long_rejected(test_client):
    """Any message content over 500 chars should fail validation."""
    response = test_client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "x" * 501}]},
    )
    assert response.status_code == 422
