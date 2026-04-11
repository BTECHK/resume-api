# ADR-0003: Chose Gemini 2.5 Flash via google-genai SDK

**Status:** Accepted
**Phase:** 4
**Date:** 2026-04-11

## Context

This decision was made while building the resume-api portfolio project, a three-version progression of recruiter interaction surfaces (REST API, email bot, chatbot) sharing a single Gemini-backed AI service.

## Decision

Answer generation uses Gemini 2.5 Flash accessed via the google-genai Python SDK (not the older google-generativeai package, which was deprecated in November 2025). Gemini 2.5 Flash was chosen for its free tier, sub-second latency on short prompts, and strong instruction-following for RAG-style grounded answers.

## Consequences

- Embedded in the ai-service RAG knowledge base via adr_content.py so the chatbot can answer architecture questions about its own system without hallucinating.
- Tradeoff accepted as part of the overall V1 to V3 progression story; see README Version Progression section.

## Source

Authored in ai-service/adr_content.py entry #3. This ADR is the long-form version; the RAG ingested form is the short content paragraph above.
