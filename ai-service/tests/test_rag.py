"""Test stubs for rag.py — expanded in Phase 7."""


def test_rag_module_imports():
    """Verify rag.py can be imported without errors."""
    from rag import ResumeRAG, get_rag, chunk_text
    assert ResumeRAG is not None
    assert callable(get_rag)
    assert callable(chunk_text)


def test_embedding_model_is_correct():
    """Verify the embedding model matches what's baked into the Docker image."""
    from rag import EMBEDDING_MODEL
    assert EMBEDDING_MODEL == "paraphrase-MiniLM-L3-v2"


def test_chunk_text_splits():
    """Verify chunk_text produces non-empty chunks."""
    from rag import chunk_text
    text = "Hello world. " * 100
    chunks = chunk_text(text)
    assert len(chunks) > 0
    assert all(len(chunk) > 0 for chunk in chunks)
