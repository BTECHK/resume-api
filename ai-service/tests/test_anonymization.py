"""Anonymization verification tests — TEST-01 explicit requirement.

Scans runtime Python modules (prompts.py, resume_data.py, interview_qa.py,
adr_content.py) for any PII deny-list terms. This is the runtime mirror of
scripts/check-anonymization.sh that runs in the pytest suite.
"""

from pathlib import Path

import pytest

AI_SERVICE_ROOT = Path(__file__).parent.parent

RUNTIME_MODULES = [
    "prompts.py",
    "resume_data.py",
    "interview_qa.py",
    "adr_content.py",
    "unanswered.py",
    "rag.py",
    "main.py",
]

DENY_PATTERNS = [
    "the candidate",
    "Candidate",
    "the candidate.candidate",
    "linkedin.com/in/candidate-profile",
]

# Employer/client names — must NOT appear in runtime modules (resume_data is
# runtime, scrub.py is a CLI tool and exempted from this sweep)
EMPLOYER_DENY = [
    "Deloitte",
    "Consulting Firm B",
    "Healthcare Program",
    "Financial Services Program",
]


@pytest.mark.parametrize("module_name", RUNTIME_MODULES)
def test_runtime_module_free_of_pii(module_name):
    """Every runtime Python module must be free of real PII."""
    module_path = AI_SERVICE_ROOT / module_name
    assert module_path.exists(), f"{module_name} missing from ai-service"
    content = module_path.read_text(encoding="utf-8", errors="replace").lower()
    for term in DENY_PATTERNS:
        assert term.lower() not in content, (
            f"{module_name} contains PII term: {term}"
        )


@pytest.mark.parametrize("module_name", RUNTIME_MODULES)
def test_runtime_module_free_of_employer_names(module_name):
    """Runtime modules must not name real employers or clients."""
    module_path = AI_SERVICE_ROOT / module_name
    content = module_path.read_text(encoding="utf-8", errors="replace")
    for term in EMPLOYER_DENY:
        assert term not in content, (
            f"{module_name} contains employer name: {term}"
        )


def test_prompts_has_expected_constants():
    """prompts.py should expose the three system prompts."""
    from prompts import SYSTEM_PROMPT, EMAIL_SYSTEM_PROMPT, CHAT_SYSTEM_PROMPT
    assert isinstance(SYSTEM_PROMPT, str)
    assert isinstance(EMAIL_SYSTEM_PROMPT, str)
    assert isinstance(CHAT_SYSTEM_PROMPT, str)
    assert len(SYSTEM_PROMPT) > 100
    assert len(EMAIL_SYSTEM_PROMPT) > 100
    assert len(CHAT_SYSTEM_PROMPT) > 100


def test_prompts_refer_to_the_candidate_not_real_name():
    """Every prompt must use the anonymized 'candidate' phrasing."""
    from prompts import SYSTEM_PROMPT, EMAIL_SYSTEM_PROMPT, CHAT_SYSTEM_PROMPT
    for prompt in (SYSTEM_PROMPT, EMAIL_SYSTEM_PROMPT, CHAT_SYSTEM_PROMPT):
        assert "candidate" in prompt.lower()


def test_resume_data_get_text_non_empty():
    """resume_data.get_resume_as_text() should return a non-trivial string."""
    from resume_data import get_resume_as_text
    text = get_resume_as_text()
    assert isinstance(text, str)
    assert len(text) > 500


def test_resume_data_anonymized():
    """get_resume_as_text() output must be anonymized."""
    from resume_data import get_resume_as_text
    text = get_resume_as_text().lower()
    for term in [t.lower() for t in DENY_PATTERNS]:
        assert term not in text, f"resume_data output contains: {term}"


def test_resume_data_sections_structure():
    """RESUME_SECTIONS should have expected top-level keys."""
    from resume_data import RESUME_SECTIONS
    for key in ("contact", "summary", "skills"):
        assert key in RESUME_SECTIONS
    contact = RESUME_SECTIONS["contact"]
    assert "name" in contact
    # Name must be the anonymized placeholder, not a real person
    assert contact["name"] == "The Candidate"
