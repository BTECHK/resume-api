"""Test stubs for main.py (ai-service endpoints) — expanded in Phase 7.

NOTE: These tests verify main.py can be parsed and its models are correct.
Full endpoint integration tests require Gemini API mocking (Phase 7).
"""

import ast


def test_main_module_parses():
    """Verify main.py has valid Python syntax."""
    with open("main.py") as f:
        tree = ast.parse(f.read())
    names = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert "lifespan" in names, "Missing lifespan function"
    assert "ask" in names, "Missing /ai/ask route"
    assert "chat" in names, "Missing /chat route"
    assert "health" in names, "Missing /health route"


def test_rate_limits_configured():
    """Verify rate limit decorators exist in main.py."""
    with open("main.py") as f:
        content = f.read()
    assert "10/minute" in content, "Missing /ai/ask rate limit"
    assert "30/minute" in content, "Missing /chat rate limit"
