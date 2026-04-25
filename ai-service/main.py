"""
Resume AI Service — FastAPI application.

Endpoints:
  POST /ai/ask  — Single-turn RAG Q&A (RAG-01)
  POST /chat    — Multi-turn conversation (CHAT-04)
  GET  /health  — Service health check

Security:
  - IP-based rate limiting via slowapi (SEC-01)
  - Prompt injection detection (SEC-02)
  - Input validation via Pydantic (SEC-03)
  - CORS configuration (SEC-06)
  - Response sanitization (SEC-09)
  - Safe error responses (SEC-07)
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator, ConfigDict
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from rag import get_rag
from security import (
    check_injection,
    flag_ip,
    is_flagged,
    sanitize_response,
    safe_error_response,
)
from gcp_secrets import get_gemini_key  # NOTE: gcp_secrets.py, NOT stdlib secrets module
from prompts import SYSTEM_PROMPT, CHAT_SYSTEM_PROMPT
from unanswered import log_unanswered, is_low_confidence

# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────

load_dotenv()  # Load .env for local development

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Rate limiter — request: Request must be FIRST parameter in route functions
limiter = Limiter(key_func=get_remote_address)

# Gemini client — initialized lazily in lifespan, stored here
_genai_client = None
_startup_ready = False  # True once RAG + Gemini are initialized


def get_genai_client():
    """Get the cached Gemini client. Must be called after lifespan startup."""
    global _genai_client
    if _genai_client is None:
        from google import genai
        api_key = get_gemini_key()
        _genai_client = genai.Client(api_key=api_key)
        logger.info("Gemini client initialized")
    return _genai_client


# ──────────────────────────────────────────────────────────────
# Lifespan (startup/shutdown)
# ──────────────────────────────────────────────────────────────

async def _warm_up():
    """Background task: load Gemini client + RAG so the first request is fast.

    Runs AFTER uvicorn is already listening, so Cloud Run's startup probe
    sees the port open immediately and doesn't kill the container.
    """
    global _startup_ready
    try:
        loop = asyncio.get_running_loop()

        logger.info("Warm-up: initializing Gemini client...")
        await loop.run_in_executor(None, get_genai_client)
        logger.info("Warm-up: Gemini client ready, loading RAG...")
        await loop.run_in_executor(None, get_rag)

        rag = get_rag()
        chunk_count = rag.collection.count()
        logger.info("RAG ready with %d chunks", chunk_count)
        _startup_ready = True
        logger.info("AI service fully warmed up")
    except Exception as exc:
        logger.error("Warm-up FAILED — service will stay in warming_up state: %s", exc, exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: kick off background warm-up, yield immediately so port opens."""
    logger.info("Starting AI service on port %s ...", os.environ.get("PORT", "8080"))
    asyncio.create_task(_warm_up())
    yield
    logger.info("AI service shutting down")


# ──────────────────────────────────────────────────────────────
# FastAPI App
# ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="Resume AI Service",
    version="1.0.0",
    description="AI-powered resume Q&A with RAG retrieval and Gemini generation",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    client_ip = get_remote_address(request)
    logger.warning("Rate limit exceeded | ip=%s | path=%s", client_ip, request.url.path)
    return safe_error_response(429)


app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

# CORS — per SEC-06, locked to specific origins via env var
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────
# Global Exception Handler (SEC-07)
# ──────────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions — never leak internals."""
    logger.error("Unhandled exception: %s", str(exc), exc_info=True)
    return safe_error_response(500)


# ──────────────────────────────────────────────────────────────
# Request/Response Models (SEC-03)
# ──────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    """Request body for POST /ai/ask."""
    question: str

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        v = v.strip()
        if len(v) == 0:
            raise ValueError("Question cannot be empty")
        if len(v) > 500:
            raise ValueError("Question cannot exceed 500 characters")
        return v


class AskResponse(BaseModel):
    """Response body for POST /ai/ask — per D-01."""
    answer: str
    sources: list[dict]
    model_used: str = "gemini-2.5-flash"


class ChatMessage(BaseModel):
    """A single message in conversation history."""
    role: Literal["user", "assistant"]
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if len(v) == 0:
            raise ValueError("Message content cannot be empty")
        if len(v) > 500:
            raise ValueError("Message content cannot exceed 500 characters")
        return v


class ChatRequest(BaseModel):
    """Request body for POST /chat — per D-06."""
    messages: list[ChatMessage]

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: list) -> list:
        if len(v) == 0:
            raise ValueError("Messages list cannot be empty")
        if len(v) > 10:
            raise ValueError("Conversation history cannot exceed 10 messages")
        if v[-1].role != "user":
            raise ValueError("Last message must be from the user")
        return v


class ChatResponse(BaseModel):
    """Response body for POST /chat — per D-02."""
    answer: str
    sources: list[dict]
    model_used: str = "gemini-2.5-flash"
    message_count: int


# ──────────────────────────────────────────────────────────────
# Injection Check Helper
# ──────────────────────────────────────────────────────────────

CANNED_DEFLECTION = (
    "I can only answer questions about the candidate's professional "
    "background, skills, experience, and qualifications."
)


def _check_and_handle_injection(text: str, request: Request) -> JSONResponse | None:
    """Check text for injection. Returns canned response if detected, else None.

    Per D-03: returns HTTP 429 with deflection (attacker sees rate limit, not security detection).
    Per D-04: flags the IP for rate reduction.
    Per D-05: logs IP + pattern name, NOT full payload.
    """
    matched = check_injection(text)
    if matched:
        client_ip = get_remote_address(request)
        flag_ip(client_ip)
        logger.warning(
            "Injection deflected | ip=%s | pattern=%s | endpoint=%s",
            client_ip, matched, request.url.path,
        )
        return JSONResponse(
            status_code=429,
            content={
                "answer": CANNED_DEFLECTION,
                "sources": [],
                "model_used": "none",
            }
        )
    return None


# ──────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Health check — Cloud Run startup/liveness probe."""
    if not _startup_ready:
        return {"status": "warming_up"}
    rag = get_rag()
    return {
        "status": "ok",
        "index_size": rag.collection.count(),
        "model": "gemini-2.5-flash",
    }


@app.post("/ai/ask", response_model=AskResponse)
@limiter.limit("10/minute")
async def ask(request: Request, body: AskRequest):
    """Single-turn RAG Q&A endpoint (RAG-01).

    1. Check for prompt injection (SEC-02)
    2. Retrieve relevant chunks from Chroma (RAG-02, RAG-03)
    3. Generate answer via Gemini 2.5 Flash (RAG-04)
    4. Sanitize response (SEC-09)
    5. Return answer with source references (D-01)
    """
    if not _startup_ready:
        return safe_error_response(503, "Service is warming up, try again shortly")

    # Injection check — per D-03, return 429 with deflection
    injection_response = _check_and_handle_injection(body.question, request)
    if injection_response:
        return injection_response

    # Check if IP is flagged — per D-04, flagged IPs get deflection
    client_ip = get_remote_address(request)
    if is_flagged(client_ip):
        logger.info("Flagged IP deflected | ip=%s", client_ip)
        return JSONResponse(
            status_code=429,
            content={
                "answer": CANNED_DEFLECTION,
                "sources": [],
                "model_used": "none",
            }
        )

    # RAG retrieval — multi-tier (RAG-05, RAG-06)
    rag = get_rag()
    retrieval = rag.query_all(body.question, top_k=3)
    chunks = retrieval["resume_chunks"]

    # RAG-07: log weak-match questions for future KB improvement
    if is_low_confidence(retrieval["top_distance"]):
        log_unanswered(body.question, retrieval["top_distance"])

    # Build merged context — tier 1 always, then supplementary tiers when present
    context_parts = ["[RESUME FACTS]", "\n\n---\n\n".join(chunks)]
    if retrieval["interview_chunks"]:
        context_parts.append("[INTERVIEW PATTERNS — use only for behavioral questions]")
        context_parts.append("\n\n---\n\n".join(retrieval["interview_chunks"]))
    if retrieval["arch_chunks"]:
        context_parts.append("[SYSTEM ARCHITECTURE]")
        context_parts.append("\n\n---\n\n".join(retrieval["arch_chunks"]))
    context = "\n\n".join(context_parts)

    # Gemini generation
    client = get_genai_client()
    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"[CONTEXT]\n{context}\n[/CONTEXT]\n\n"
        f"Question: {body.question}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
        )
        answer = sanitize_response(response.text)
    except Exception as exc:
        logger.error("Gemini generation failed: %s", type(exc).__name__, exc_info=True)
        return safe_error_response(503, "AI generation temporarily unavailable")

    # Build source references — per D-01
    sources = [
        {"chunk": chunk[:200], "relevance": round(1.0 - (i * 0.1), 2)}
        for i, chunk in enumerate(chunks)
    ]

    return AskResponse(answer=answer, sources=sources, model_used="gemini-2.5-flash")


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("30/minute")
async def chat(request: Request, body: ChatRequest):
    """Multi-turn conversation endpoint (CHAT-04).

    Accepts up to 10 messages of conversation history (D-06).
    Reconstructs chat from history on every request (stateless).
    Last 3 messages sent verbatim; older messages summarized (D-07).
    """
    if not _startup_ready:
        return safe_error_response(503, "Service is warming up, try again shortly")

    # Injection check on the latest user message
    last_message = body.messages[-1].content
    injection_response = _check_and_handle_injection(last_message, request)
    if injection_response:
        return injection_response

    # Check flagged IP
    client_ip = get_remote_address(request)
    if is_flagged(client_ip):
        logger.info("Flagged IP deflected on /chat | ip=%s", client_ip)
        return JSONResponse(
            status_code=429,
            content={
                "answer": CANNED_DEFLECTION,
                "sources": [],
                "model_used": "none",
                "message_count": len(body.messages),
            }
        )

    # RAG retrieval using the latest user question — multi-tier (RAG-05, RAG-06)
    rag = get_rag()
    retrieval = rag.query_all(last_message, top_k=3)
    chunks = retrieval["resume_chunks"]

    # RAG-07: log weak-match questions for future KB improvement
    if is_low_confidence(retrieval["top_distance"]):
        log_unanswered(last_message, retrieval["top_distance"])

    # Build merged context
    context_parts = ["[RESUME FACTS]", "\n\n---\n\n".join(chunks)]
    if retrieval["interview_chunks"]:
        context_parts.append("[INTERVIEW PATTERNS — use only for behavioral questions]")
        context_parts.append("\n\n---\n\n".join(retrieval["interview_chunks"]))
    if retrieval["arch_chunks"]:
        context_parts.append("[SYSTEM ARCHITECTURE]")
        context_parts.append("\n\n---\n\n".join(retrieval["arch_chunks"]))
    context = "\n\n".join(context_parts)

    # Build conversation for Gemini
    client = get_genai_client()

    # Per D-07: if > 3 messages, summarize older ones
    messages = body.messages
    if len(messages) > 3:
        # Summarize messages[:-3] into a brief context string
        older_text = "\n".join(
            f"{msg.role}: {msg.content}" for msg in messages[:-3]
        )
        try:
            summary_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=(
                    "Summarize this conversation history in 2-3 sentences. "
                    "Focus on what the user has asked about so far:\n\n"
                    f"{older_text}"
                ),
            )
            conversation_summary = summary_response.text
        except Exception as exc:
            logger.warning("Gemini summarization failed, falling back to truncation: %s", type(exc).__name__, exc_info=True)
            conversation_summary = older_text[:300]

        recent_messages = messages[-3:]
        history_context = f"Previous conversation summary: {conversation_summary}\n\n"
    else:
        recent_messages = messages
        history_context = ""

    # Build the full prompt with system context, RAG context, and conversation
    conversation_text = "\n".join(
        f"{'User' if msg.role == 'user' else 'Assistant'}: {msg.content}"
        for msg in recent_messages
    )

    full_prompt = (
        f"{CHAT_SYSTEM_PROMPT}\n\n"
        f"[RESUME CONTEXT]\n{context}\n[/RESUME CONTEXT]\n\n"
        f"{history_context}"
        f"Conversation:\n{conversation_text}\n\n"
        f"Respond to the user's latest message."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
        )
        answer = sanitize_response(response.text)
    except Exception as exc:
        logger.error("Gemini chat generation failed: %s", type(exc).__name__, exc_info=True)
        return safe_error_response(503, "AI generation temporarily unavailable")

    sources = [
        {"chunk": chunk[:200], "relevance": round(1.0 - (i * 0.1), 2)}
        for i, chunk in enumerate(chunks)
    ]

    return ChatResponse(
        answer=answer,
        sources=sources,
        model_used="gemini-2.5-flash",
        message_count=len(body.messages),
    )
