# ADR-0004: Chose separate ai-service on Cloud Run, decoupled from Phase 1 REST API

**Status:** Accepted
**Phase:** 4
**Date:** 2026-04-11

## Context

This decision was made while building the resume-api portfolio project, a three-version progression of recruiter interaction surfaces (REST API, email bot, chatbot) sharing a single Gemini-backed AI service.

## Decision

The AI-powered endpoints (/ai/ask, /chat) live in a new ai-service deployed as a separate Cloud Run service, not bolted onto the existing Phase 1 resume-api service. This keeps the original REST API untouched, allows independent scaling, and prevents embedding model cold-start time from affecting the simpler REST endpoints.

## Consequences

- Embedded in the ai-service RAG knowledge base via adr_content.py so the chatbot can answer architecture questions about its own system without hallucinating.
- Tradeoff accepted as part of the overall V1 to V3 progression story; see README Version Progression section.

## Source

Authored in ai-service/adr_content.py entry #4. This ADR is the long-form version; the RAG ingested form is the short content paragraph above.
