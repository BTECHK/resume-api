"""Unit tests for unanswered.py — TEST-01 / RAG-07 coverage."""

import json


def test_unanswered_module_imports():
    """Verify unanswered.py exports expected functions and constants."""
    from unanswered import (
        log_unanswered, is_low_confidence, read_unanswered,
        CONFIDENCE_DISTANCE_THRESHOLD, MAX_QUESTION_LENGTH,
    )
    assert callable(log_unanswered)
    assert callable(is_low_confidence)
    assert callable(read_unanswered)
    assert 0.0 < CONFIDENCE_DISTANCE_THRESHOLD < 2.0
    assert MAX_QUESTION_LENGTH > 0


def test_is_low_confidence_above_threshold():
    """Distances above the threshold should count as low confidence."""
    from unanswered import is_low_confidence, CONFIDENCE_DISTANCE_THRESHOLD
    assert is_low_confidence(CONFIDENCE_DISTANCE_THRESHOLD + 0.1)
    assert is_low_confidence(1.5)


def test_is_low_confidence_below_threshold():
    """Distances below the threshold should NOT count as low confidence."""
    from unanswered import is_low_confidence, CONFIDENCE_DISTANCE_THRESHOLD
    assert not is_low_confidence(CONFIDENCE_DISTANCE_THRESHOLD - 0.1)
    assert not is_low_confidence(0.1)
    assert not is_low_confidence(0.0)


def test_log_unanswered_writes_jsonl(tmp_unanswered_log):
    """A single log call should produce a single JSONL line."""
    from unanswered import log_unanswered
    log_unanswered("What color is your bugatti?", 0.95)
    assert tmp_unanswered_log.exists()
    lines = tmp_unanswered_log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["question"] == "What color is your bugatti?"
    assert entry["top_distance"] == 0.95
    assert entry["low_confidence"] is True
    assert "ts" in entry


def test_log_unanswered_appends(tmp_unanswered_log):
    """Multiple calls should append, not overwrite."""
    from unanswered import log_unanswered, read_unanswered
    log_unanswered("q1", 0.8)
    log_unanswered("q2", 0.9)
    log_unanswered("q3", 0.75)
    entries = read_unanswered()
    assert len(entries) == 3
    assert [e["question"] for e in entries] == ["q1", "q2", "q3"]


def test_log_unanswered_truncates_long_question(tmp_unanswered_log):
    """Questions longer than MAX_QUESTION_LENGTH should be truncated."""
    from unanswered import log_unanswered, read_unanswered, MAX_QUESTION_LENGTH
    long_q = "x" * (MAX_QUESTION_LENGTH * 2)
    log_unanswered(long_q, 0.9)
    entries = read_unanswered()
    assert len(entries) == 1
    assert len(entries[0]["question"]) == MAX_QUESTION_LENGTH


def test_log_unanswered_never_raises(tmp_path, monkeypatch):
    """I/O errors must never break the main request path."""
    from unanswered import log_unanswered
    # Point at an unwritable path (a file used as a directory would fail mkdir)
    bogus = tmp_path / "nonexistent" / "deep" / "log.jsonl"
    monkeypatch.setenv("UNANSWERED_LOG_PATH", str(bogus))
    # Must not raise even though dir creation is fine; try invalid path
    monkeypatch.setenv("UNANSWERED_LOG_PATH", str(tmp_path / "actual.jsonl"))
    log_unanswered("safe question", 0.9)  # Should succeed

    # Now point to something that can't be written at all (a file, then subpath under it)
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    monkeypatch.setenv("UNANSWERED_LOG_PATH", str(blocker / "child.jsonl"))
    # Should swallow the exception, not raise
    log_unanswered("still safe", 0.9)


def test_read_unanswered_empty_when_no_file(tmp_path, monkeypatch):
    """read_unanswered should return [] when the file doesn't exist yet."""
    from unanswered import read_unanswered
    monkeypatch.setenv("UNANSWERED_LOG_PATH", str(tmp_path / "missing.jsonl"))
    assert read_unanswered() == []


def test_read_unanswered_skips_corrupt_lines(tmp_unanswered_log):
    """Corrupt JSON lines should be silently skipped."""
    from unanswered import log_unanswered, read_unanswered
    log_unanswered("valid question", 0.9)
    # Append a garbage line
    with tmp_unanswered_log.open("a", encoding="utf-8") as f:
        f.write("{not valid json\n")
        f.write("\n")  # blank line
    log_unanswered("another valid", 0.85)
    entries = read_unanswered()
    assert len(entries) == 2
    assert entries[0]["question"] == "valid question"
    assert entries[1]["question"] == "another valid"
