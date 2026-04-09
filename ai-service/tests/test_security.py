"""Test stubs for security.py — expanded in Phase 7."""


def test_security_module_imports():
    """Verify security.py exports all expected functions."""
    from security import (
        check_injection,
        flag_ip,
        is_flagged,
        sanitize_response,
        safe_error_response,
        INJECTION_PATTERNS,
    )
    assert callable(check_injection)
    assert callable(flag_ip)
    assert callable(is_flagged)
    assert callable(sanitize_response)
    assert callable(safe_error_response)
    assert len(INJECTION_PATTERNS) >= 10


def test_check_injection_detects_known_pattern(injection_question):
    """Verify injection detection catches a known pattern."""
    from security import check_injection
    result = check_injection(injection_question)
    assert result is not None


def test_check_injection_passes_safe_question(dummy_question):
    """Verify injection detection does not flag normal questions."""
    from security import check_injection
    result = check_injection(dummy_question)
    assert result is None


def test_sanitize_response_scrubs_real_name():
    """Verify response sanitization replaces real name."""
    from security import sanitize_response
    result = sanitize_response("The Candidate is a consultant")
    assert "the candidate" not in result
    assert "candidate" in result.lower()
