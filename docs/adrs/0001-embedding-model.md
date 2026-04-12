# ADR-0001: Chose paraphrase-MiniLM-L3-v2 as the embedding model

**Status:** Accepted
**Phase:** 4
**Date:** 2026-04-11

## Context

This decision was made while building the resume-api portfolio project, a three-version progression of recruiter interaction surfaces (REST API, email bot, chatbot) sharing a single Gemini-backed AI service.

## Decision

The ai-service uses paraphrase-MiniLM-L3-v2 (33MB) as its sentence embedding model. We chose this over the more common all-MiniLM-L6-v2 (420MB) specifically to minimize Cloud Run cold start time. The 33MB model is baked into the Docker image at build time and loads into memory in under 1 second on a cold container.

## Consequences

- Embedded in the ai-service RAG knowledge base via adr_content.py so the chatbot can answer architecture questions about its own system without hallucinating.
- Tradeoff accepted as part of the overall V1 to V3 progression story; see README Version Progression section.

## Source

Authored in ai-service/adr_content.py entry #1. This ADR is the long-form version; the RAG ingested form is the short content paragraph above.

## Addendum (2026-04-12): Vendored weights

After ~10 Cloud Build failures caused by HuggingFace Hub rate-limiting GCP's
shared egress IPs (the download step would stall and exceed the 30-min build
timeout), the MiniLM weights were vendored into the repo at
`ai-service/model/paraphrase-MiniLM-L3-v2/`. The Dockerfile `COPY`s them in
and sets `TRANSFORMERS_OFFLINE=1` / `HF_HUB_OFFLINE=1` so `sentence-transformers`
never calls the Hub. Trade-off: ~68MB added to the repo in exchange for
deterministic, offline-capable builds. Model updates are a deliberate, reviewed
action via `scripts/vendor_model.sh` rather than a silent dependency fetch.
