"""Unit tests for scrub.py — TEST-01 anonymization coverage.

Exercises scrub_text() and scrub_filename() in isolation. The CLI entry
point (main) is excluded from coverage via .coveragerc.
"""


def test_scrub_module_imports():
    """scrub.py must export the functions used by tests."""
    from scrub import scrub_text, scrub_filename, COMPANY_REPLACEMENTS, PII_REPLACEMENTS, INTERVIEWER_PATTERNS
    assert callable(scrub_text)
    assert callable(scrub_filename)
    assert isinstance(COMPANY_REPLACEMENTS, dict)
    assert isinstance(PII_REPLACEMENTS, dict)
    assert isinstance(INTERVIEWER_PATTERNS, list)


def test_scrub_replaces_deloitte():
    """Deloitte should be replaced with the canonical descriptor."""
    from scrub import scrub_text
    result = scrub_text("I worked at Deloitte on a client project.")
    assert "Deloitte" not in result
    assert "Big Four" in result


def test_scrub_replaces_real_name():
    """Real name variations should be replaced with 'the candidate'."""
    from scrub import scrub_text
    for variant in ["The Candidate", "The Candidate"]:
        result = scrub_text(f"{variant} led the team.")
        assert "Candidate" not in result
        assert "the candidate" in result


def test_scrub_replaces_phone():
    """Phone numbers should be replaced."""
    from scrub import scrub_text
    result = scrub_text("Reach me at 555-123-4567 for details.")
    assert "555-123-4567" not in result
    assert "[PHONE REDACTED]" in result


def test_scrub_replaces_email():
    """Email addresses should be replaced."""
    from scrub import scrub_text
    result = scrub_text("Contact: person@example.com")
    assert "person@example.com" not in result
    assert "[EMAIL REDACTED]" in result


def test_scrub_replaces_linkedin():
    """LinkedIn URLs should be replaced."""
    from scrub import scrub_text
    result = scrub_text("Profile: https://linkedin.com/in/someone-real")
    assert "linkedin.com/in/someone-real" not in result
    assert "[LINKEDIN REDACTED]" in result


def test_scrub_replaces_clearance():
    """Clearance levels should be scrubbed."""
    from scrub import scrub_text
    for phrase in ["Top Secret/SCI", "TS/SCI", "Secret clearance"]:
        result = scrub_text(f"The candidate holds a {phrase}.")
        assert "[CLEARANCE LEVEL]" in result


def test_scrub_replaces_multiple_companies():
    """Multiple company mentions in the same text should all be replaced."""
    from scrub import scrub_text
    input_text = "Worked at Meta, Google, and Boeing over 5 years."
    result = scrub_text(input_text)
    assert "Meta" not in result
    assert "Google" not in result
    assert "Boeing" not in result
    # Descriptors should be present
    assert "social media" in result
    assert "technology company" in result
    assert "aerospace" in result


def test_scrub_replaces_interviewer_names():
    """Interviewer names in the list should be replaced with 'the interviewer'."""
    from scrub import scrub_text
    result = scrub_text("Yev asked great questions about system design.")
    assert "Yev" not in result
    assert "the interviewer" in result


def test_scrub_removes_otter_attribution():
    """Lines containing Otter AI attribution should be removed."""
    from scrub import scrub_text
    input_text = (
        "Normal content line.\n"
        "Transcribed by otter.ai\n"
        "Another normal line.\n"
    )
    result = scrub_text(input_text)
    assert "otter.ai" not in result.lower()
    assert "Normal content line." in result
    assert "Another normal line." in result


def test_scrub_collapses_blank_lines():
    """Three or more blank lines should collapse to two."""
    from scrub import scrub_text
    input_text = "First.\n\n\n\n\nSecond."
    result = scrub_text(input_text)
    assert "\n\n\n" not in result


def test_scrub_filename_removes_companies():
    """scrub_filename should remove company names."""
    from scrub import scrub_filename
    result = scrub_filename("Deloitte_interview_2024")
    assert "Deloitte" not in result


def test_scrub_filename_removes_interviewer_names():
    """scrub_filename should remove interviewer names."""
    from scrub import scrub_filename
    result = scrub_filename("Yev_first_round_interview")
    assert "Yev" not in result


def test_scrub_filename_removes_otter_suffix():
    """scrub_filename should strip the _otter_ai marker."""
    from scrub import scrub_filename
    result = scrub_filename("interview_transcript_otter_ai")
    assert "otter_ai" not in result


def test_scrub_filename_fallback_on_empty():
    """If all content is stripped, scrub_filename should return a default."""
    from scrub import scrub_filename
    result = scrub_filename("")
    assert result == "interview_transcript"
