# ADR-0012: Chose direct CORS from chatbot to ai-service (no reverse proxy)

**Status:** Accepted
**Phase:** 6
**Date:** 2026-04-11

## Context

This decision was made while building the resume-api portfolio project, a three-version progression of recruiter interaction surfaces (REST API, email bot, chatbot) sharing a single Gemini-backed AI service.

## Decision

The React chatbot calls the ai-service Cloud Run URL directly via CORS rather than through a reverse proxy on the frontend's Nginx. The ai-service has ALLOWED_ORIGINS locked to the chatbot's Cloud Run URL. This keeps the deployment simpler at the cost of a chicken-and-egg CORS update after initial deploy (handled in DEFERRED-WORK.md).

## Consequences

- Embedded in the ai-service RAG knowledge base via adr_content.py so the chatbot can answer architecture questions about its own system without hallucinating.
- Tradeoff accepted as part of the overall V1 to V3 progression story; see README Version Progression section.

## Source

Authored in ai-service/adr_content.py entry #12. This ADR is the long-form version; the RAG ingested form is the short content paragraph above.
