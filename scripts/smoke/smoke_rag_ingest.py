#!/usr/bin/env python3
"""Smoke test: resume data → RAG ingestion → retrieval → generation (INT-03).

Runs the RAG bootstrap path in-process against a real Chroma ephemeral
client. Intended to be run inside the ai-service container or a dev
environment where all Python dependencies are installed. Does not hit
Gemini.
"""

import os
import sys


def main() -> int:
    ai_service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ai-service"))
    if ai_service_dir not in sys.path:
        sys.path.insert(0, ai_service_dir)

    try:
        from rag import get_rag
    except ImportError as exc:
        print(f"RUN-DEFERRED: ai-service deps not installed ({exc}). "
              f"Run `pip install -r ai-service/requirements.txt` first.")
        return 2

    rag = get_rag()
    count = rag.collection.count()
    if count <= 0:
        print(f"FAIL: RAG ingestion produced 0 chunks")
        return 1

    chunks = rag.query("What certifications does the candidate have?", top_k=3)
    if not chunks:
        print(f"FAIL: RAG query returned 0 chunks for a factual question")
        return 1

    print(f"PASS: RAG ingested {count} chunks, query returned {len(chunks)} matches")
    print(f"      top chunk preview: {chunks[0][:120]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
