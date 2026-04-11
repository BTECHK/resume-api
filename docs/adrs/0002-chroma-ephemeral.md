# ADR-0002: Chose Chroma with ephemeral in-memory client

**Status:** Accepted
**Phase:** 4
**Date:** 2026-04-11

## Context

This decision was made while building the resume-api portfolio project, a three-version progression of recruiter interaction surfaces (REST API, email bot, chatbot) sharing a single Gemini-backed AI service.

## Decision

The ai-service uses Chroma as its vector database in ephemeral (in-memory) mode. On every cold start, it re-ingests the bundled resume data from resume_data.py into a fresh collection. This avoids persistent-volume complexity on Cloud Run and keeps the service stateless — any instance can serve any request without session affinity.

## Consequences

- Embedded in the ai-service RAG knowledge base via adr_content.py so the chatbot can answer architecture questions about its own system without hallucinating.
- Tradeoff accepted as part of the overall V1 to V3 progression story; see README Version Progression section.

## Source

Authored in ai-service/adr_content.py entry #2. This ADR is the long-form version; the RAG ingested form is the short content paragraph above.
