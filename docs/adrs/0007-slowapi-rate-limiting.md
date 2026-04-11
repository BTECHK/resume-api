# ADR-0007: Chose IP-based rate limiting via slowapi

**Status:** Accepted
**Phase:** 4
**Date:** 2026-04-11

## Context

This decision was made while building the resume-api portfolio project, a three-version progression of recruiter interaction surfaces (REST API, email bot, chatbot) sharing a single Gemini-backed AI service.

## Decision

Rate limiting uses slowapi, configured at 10 requests/minute on /ai/ask and 30 requests/minute on /chat. Flagged IPs (those that trigger prompt injection detection) get additional dynamic reduction for 5 minutes. This prevents abuse while keeping the latency overhead negligible for normal users.

## Consequences

- Embedded in the ai-service RAG knowledge base via adr_content.py so the chatbot can answer architecture questions about its own system without hallucinating.
- Tradeoff accepted as part of the overall V1 to V3 progression story; see README Version Progression section.

## Source

Authored in ai-service/adr_content.py entry #7. This ADR is the long-form version; the RAG ingested form is the short content paragraph above.
