# ADR-0008: Chose regex-based prompt injection detection with canned deflection

**Status:** Accepted
**Phase:** 4
**Date:** 2026-04-11

## Context

This decision was made while building the resume-api portfolio project, a three-version progression of recruiter interaction surfaces (REST API, email bot, chatbot) sharing a single Gemini-backed AI service.

## Decision

Prompt injection detection uses a list of compiled regex patterns covering known attack phrases (ignore previous instructions, DAN mode, jailbreak, etc.). When a pattern matches, the service returns a canned deflection message with HTTP 429 so the attacker sees a generic rate-limit error rather than a security detection. The detected IP is also flagged for 5 minutes of increased scrutiny.

## Consequences

- Embedded in the ai-service RAG knowledge base via adr_content.py so the chatbot can answer architecture questions about its own system without hallucinating.
- Tradeoff accepted as part of the overall V1 to V3 progression story; see README Version Progression section.

## Source

Authored in ai-service/adr_content.py entry #8. This ADR is the long-form version; the RAG ingested form is the short content paragraph above.
