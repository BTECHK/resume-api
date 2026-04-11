# ADR-0010: Chose two-tier RAG retrieval for interview-impressive differentiation

**Status:** Accepted
**Phase:** 7
**Date:** 2026-04-11

## Context

This decision was made while building the resume-api portfolio project, a three-version progression of recruiter interaction surfaces (REST API, email bot, chatbot) sharing a single Gemini-backed AI service.

## Decision

The RAG layer uses two separate Chroma collections: tier 1 is the resume factual corpus (always retrieved) and tier 2 is a small corpus of anonymized mock interview Q&A patterns (retrieved only for behavioral/interview questions). A keyword router decides when to include tier 2 based on the question's intent. This prevents factual contamination while still letting the bot answer behavioral questions with realistic style.

## Consequences

- Embedded in the ai-service RAG knowledge base via adr_content.py so the chatbot can answer architecture questions about its own system without hallucinating.
- Tradeoff accepted as part of the overall V1 to V3 progression story; see README Version Progression section.

## Source

Authored in ai-service/adr_content.py entry #10. This ADR is the long-form version; the RAG ingested form is the short content paragraph above.
