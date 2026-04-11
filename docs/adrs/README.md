# Architecture Decision Records

This directory contains one markdown file per major architecture decision made while building the resume-api portfolio project. Each ADR follows the standard Context / Decision / Consequences format.

The same decisions are also embedded in short form inside `ai-service/adr_content.py` so the chatbot can answer architecture questions about its own system from grounded RAG context.

## Index

| # | Decision | Phase |
|---|---|---|
| 0001 | [Chose paraphrase-MiniLM-L3-v2 as the embedding model](0001-embedding-model.md) | 4 |
| 0002 | [Chose Chroma with ephemeral in-memory client](0002-chroma-ephemeral.md) | 4 |
| 0003 | [Chose Gemini 2.5 Flash via google-genai SDK](0003-gemini-25-flash.md) | 4 |
| 0004 | [Chose separate ai-service on Cloud Run](0004-separate-ai-service.md) | 4 |
| 0005 | [Chose n8n self-hosted on e2-micro for the email bot](0005-n8n-e2-micro.md) | 5 |
| 0006 | [Chose React 19 + Vite 8 + Tailwind v4 for the chatbot frontend](0006-react-vite-tailwind.md) | 6 |
| 0007 | [Chose IP-based rate limiting via slowapi](0007-slowapi-rate-limiting.md) | 4 |
| 0008 | [Chose regex-based prompt injection detection](0008-regex-injection-detection.md) | 4 |
| 0009 | [Chose GCP Secret Manager for all runtime secrets](0009-secret-manager.md) | 4 |
| 0010 | [Chose two-tier RAG retrieval](0010-two-tier-rag.md) | 7 |
| 0011 | [Chose file-based JSONL logging for unanswered questions](0011-jsonl-unanswered-logging.md) | 7 |
| 0012 | [Chose direct CORS from chatbot to ai-service](0012-direct-cors.md) | 6 |
