"""Unit tests for rag.py — TEST-01, RAG-05/06 coverage."""

import pytest

# rag.py imports chromadb and sentence_transformers at module load; when the
# heavy ML deps aren't installed locally, skip the whole module. CI installs
# requirements.txt so the full suite runs there.
pytest.importorskip("chromadb")
pytest.importorskip("sentence_transformers")


def test_rag_module_imports():
    """Verify rag.py exports all expected symbols."""
    from rag import (
        ResumeRAG, get_rag, chunk_text,
        needs_interview_tier, needs_architecture_tier,
        EMBEDDING_MODEL, COLLECTION_NAME,
        INTERVIEW_COLLECTION_NAME, ARCH_COLLECTION_NAME,
        ARCH_KEYWORDS, INTERVIEW_KEYWORDS,
    )
    assert ResumeRAG is not None
    assert callable(get_rag)
    assert callable(chunk_text)
    assert callable(needs_interview_tier)
    assert callable(needs_architecture_tier)


def test_embedding_model_is_correct():
    """Verify the embedding model matches what's baked into the Docker image."""
    from rag import EMBEDDING_MODEL
    assert EMBEDDING_MODEL == "paraphrase-MiniLM-L3-v2"


def test_collection_names_distinct():
    """All three collections must have unique names."""
    from rag import COLLECTION_NAME, INTERVIEW_COLLECTION_NAME, ARCH_COLLECTION_NAME
    names = {COLLECTION_NAME, INTERVIEW_COLLECTION_NAME, ARCH_COLLECTION_NAME}
    assert len(names) == 3


def test_chunk_text_splits():
    """Verify chunk_text produces non-empty chunks."""
    from rag import chunk_text
    text = "Hello world. " * 100
    chunks = chunk_text(text)
    assert len(chunks) > 0
    assert all(len(chunk) > 0 for chunk in chunks)


def test_chunk_text_respects_chunk_size():
    """Every chunk should be roughly bounded by CHUNK_SIZE."""
    from rag import chunk_text, CHUNK_SIZE
    text = ("Line number with some content.\n" * 200)
    chunks = chunk_text(text)
    # Allow ~2x CHUNK_SIZE for overlap + last line carry; hard fail at 4x
    assert all(len(chunk) < CHUNK_SIZE * 4 for chunk in chunks)


def test_chunk_text_empty_string_returns_empty():
    """Empty input should produce empty output, not crash."""
    from rag import chunk_text
    chunks = chunk_text("")
    assert chunks == []


def test_chunk_text_single_line_short():
    """Short text should produce a single chunk."""
    from rag import chunk_text
    chunks = chunk_text("Just one short sentence.")
    assert len(chunks) == 1
    assert "short sentence" in chunks[0]


def test_needs_interview_tier_positive():
    """Behavioral questions should route to tier 2."""
    from rag import needs_interview_tier
    assert needs_interview_tier("Tell me about a time you failed")
    assert needs_interview_tier("What's your biggest weakness?")
    assert needs_interview_tier("Describe a leadership conflict")


def test_needs_interview_tier_negative():
    """Factual questions should NOT route to tier 2."""
    from rag import needs_interview_tier
    assert not needs_interview_tier("What certifications does the candidate have?")
    assert not needs_interview_tier("What programming languages does the candidate know?")
    assert not needs_interview_tier("How many years of experience in Python?")


def test_needs_architecture_tier_positive():
    """Architecture questions should route to the arch collection."""
    from rag import needs_architecture_tier
    assert needs_architecture_tier("What is the tech stack?")
    assert needs_architecture_tier("How is this deployed?")
    assert needs_architecture_tier("What embedding model is used?")


def test_needs_architecture_tier_negative():
    """Non-architecture questions should not trigger the arch tier."""
    from rag import needs_architecture_tier
    assert not needs_architecture_tier("What is the candidate's work history?")
    assert not needs_architecture_tier("Tell me about past projects")


def test_interview_patterns_module_exports():
    """interview_qa.py must expose the tier-2 corpus."""
    from loader import _load_yaml, get_interview_patterns_as_text
    patterns = _load_yaml("interview_qa")
    assert isinstance(patterns, list)
    assert len(patterns) >= 10
    text = get_interview_patterns_as_text()
    assert "INTERVIEW PATTERN" in text
    for item in patterns:
        assert "question" in item
        assert "response_pattern" in item
        assert "tags" in item


def test_interview_patterns_anonymized(pii_name_variants):
    """Tier-2 corpus must be fully anonymized."""
    from conftest import _load_employer_deny
    from loader import get_interview_patterns_as_text
    text = get_interview_patterns_as_text().lower()
    forbidden = [t.lower() for t in _load_employer_deny()]
    if pii_name_variants:
        forbidden.extend(name.lower() for name, _ in pii_name_variants)
    if not forbidden:
        pytest.skip("No deny terms available")
    for term in forbidden:
        assert term not in text, f"Tier-2 corpus contains forbidden term: {term}"


def test_adr_content_module_exports():
    """adr_content.py must expose architecture facts."""
    from loader import _load_yaml, get_adr_content_as_text
    adr_data = _load_yaml("adr")
    assert isinstance(adr_data, list)
    assert len(adr_data) >= 10
    text = get_adr_content_as_text()
    assert "ARCHITECTURE DECISION" in text
    for item in adr_data:
        assert "decision" in item
        assert "content" in item


def test_adr_content_mentions_key_tech():
    """Architecture content should reference the key stack components."""
    from loader import get_adr_content_as_text
    text = get_adr_content_as_text().lower()
    assert "gemini" in text
    assert "chroma" in text
    assert "cloud run" in text
    assert "paraphrase-minilm" in text
    assert "slowapi" in text


def test_adr_content_anonymized(pii_name_variants):
    """ADR content must not contain real names or employers."""
    from conftest import _load_employer_deny
    from loader import get_adr_content_as_text
    text = get_adr_content_as_text().lower()
    forbidden = [t.lower() for t in _load_employer_deny()]
    if pii_name_variants:
        forbidden.extend(name.lower() for name, _ in pii_name_variants)
    if not forbidden:
        pytest.skip("No deny terms available")
    for term in forbidden:
        assert term not in text, f"ADR content contains forbidden term: {term}"


def test_rag_query_routing_logic():
    """Verify _that the keyword routing works without needing Chroma."""
    from rag import needs_interview_tier, needs_architecture_tier
    # Pure factual — no tiers
    assert not needs_interview_tier("What certifications?")
    assert not needs_architecture_tier("What certifications?")
    # Architecture question — arch only
    q = "What is the tech stack?"
    assert needs_architecture_tier(q)
    assert not needs_interview_tier(q)
    # Behavioral question — interview only
    q = "Tell me about a time you showed leadership"
    assert needs_interview_tier(q)
    assert not needs_architecture_tier(q)
