# ADR-0005: Chose n8n self-hosted on e2-micro for the email bot

**Status:** Accepted
**Phase:** 5
**Date:** 2026-04-11

## Context

This decision was made while building the resume-api portfolio project, a three-version progression of recruiter interaction surfaces (REST API, email bot, chatbot) sharing a single Gemini-backed AI service.

## Decision

The email-to-AI bot runs on a self-hosted n8n instance on a GCE e2-micro (1 vCPU, 1GB RAM) with a 2GB swap file, Docker mem_limit of 700MB, and systemd auto-restart. Gmail OAuth is in Production mode (not Test) to prevent the 7-day token expiry that would otherwise require weekly manual re-auth. Polling interval is 5 minutes.

## Consequences

- Embedded in the ai-service RAG knowledge base via adr_content.py so the chatbot can answer architecture questions about its own system without hallucinating.
- Tradeoff accepted as part of the overall V1 to V3 progression story; see README Version Progression section.

## Source

Authored in ai-service/adr_content.py entry #5. This ADR is the long-form version; the RAG ingested form is the short content paragraph above.
