"""Tests for the YAML-backed content loader."""

import pytest


def test_resume_text_contains_expected_sections():
    from loader import get_resume_as_text

    text = get_resume_as_text()
    assert "Professional Summary" in text
    assert "Skills" in text
    assert "Certifications" in text


def test_resume_dict_has_expected_keys():
    from loader import get_resume_dict

    data = get_resume_dict()
    for key in ("contact", "summary", "skills", "experience", "education", "certifications"):
        assert key in data, f"Missing key: {key}"


def test_interview_patterns_non_empty():
    from loader import get_interview_patterns_as_text

    text = get_interview_patterns_as_text()
    assert len(text) > 100


def test_adr_content_has_phase_markers():
    from loader import get_adr_content_as_text

    text = get_adr_content_as_text()
    assert "phase" in text.lower()


def test_loader_is_cached():
    from loader import _load_yaml

    info = _load_yaml.cache_info()
    assert info is not None
