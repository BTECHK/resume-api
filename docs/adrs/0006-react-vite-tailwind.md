# ADR-0006: Chose React 19 + Vite 8 + Tailwind v4 for the chatbot frontend

**Status:** Accepted
**Phase:** 6
**Date:** 2026-04-11

## Context

This decision was made while building the resume-api portfolio project, a three-version progression of recruiter interaction surfaces (REST API, email bot, chatbot) sharing a single Gemini-backed AI service.

## Decision

The recruiter-facing chatbot is a React 19.2 + Vite 8.0 + TypeScript + Tailwind v4.2 single-page app, deployed as a multi-stage Docker image (Node build stage, Nginx serve stage) on Cloud Run. It calls the ai-service /chat endpoint directly via CORS; there is no reverse proxy or same-origin mount. Design follows Apple Human Interface guidelines — system font stack, generous whitespace, rounded-2xl cards.

## Consequences

- Embedded in the ai-service RAG knowledge base via adr_content.py so the chatbot can answer architecture questions about its own system without hallucinating.
- Tradeoff accepted as part of the overall V1 to V3 progression story; see README Version Progression section.

## Source

Authored in ai-service/adr_content.py entry #6. This ADR is the long-form version; the RAG ingested form is the short content paragraph above.
