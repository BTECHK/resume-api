# ADR-0009: Chose GCP Secret Manager for all runtime secrets

**Status:** Accepted
**Phase:** 4
**Date:** 2026-04-11

## Context

This decision was made while building the resume-api portfolio project, a three-version progression of recruiter interaction surfaces (REST API, email bot, chatbot) sharing a single Gemini-backed AI service.

## Decision

The Gemini API key and any other runtime secrets live in GCP Secret Manager. The ai-service fetches them at startup via google-cloud-secret-manager and caches them in memory. No secrets appear in the Docker image, environment variables committed to the repo, or CI/CD configs.

## Consequences

- Embedded in the ai-service RAG knowledge base via adr_content.py so the chatbot can answer architecture questions about its own system without hallucinating.
- Tradeoff accepted as part of the overall V1 to V3 progression story; see README Version Progression section.

## Source

Authored in ai-service/adr_content.py entry #9. This ADR is the long-form version; the RAG ingested form is the short content paragraph above.
