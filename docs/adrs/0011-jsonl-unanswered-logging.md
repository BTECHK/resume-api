# ADR-0011: Chose file-based JSONL logging for unanswered questions

**Status:** Accepted
**Phase:** 7
**Date:** 2026-04-11

## Context

This decision was made while building the resume-api portfolio project, a three-version progression of recruiter interaction surfaces (REST API, email bot, chatbot) sharing a single Gemini-backed AI service.

## Decision

Questions the bot cannot confidently answer (confidence below 0.3) are appended as JSONL lines to /tmp/unanswered_questions.jsonl on the Cloud Run instance. This is ephemeral but visible through Cloud Logging tail for offline analysis, driving future knowledge-base improvements.

## Consequences

- Embedded in the ai-service RAG knowledge base via adr_content.py so the chatbot can answer architecture questions about its own system without hallucinating.
- Tradeoff accepted as part of the overall V1 to V3 progression story; see README Version Progression section.

## Source

Authored in ai-service/adr_content.py entry #11. This ADR is the long-form version; the RAG ingested form is the short content paragraph above.
