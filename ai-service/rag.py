"""
RAG (Retrieval-Augmented Generation) module.
Handles document chunking, embedding, vector storage, and retrieval.
"""

import os
import logging
from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer

from loader import get_resume_as_text, get_interview_patterns_as_text, get_adr_content_as_text

logger = logging.getLogger(__name__)

# Embedding model — runs locally, no API key needed.
# paraphrase-MiniLM-L3-v2 weights are vendored in ./model/ (see ADR-0001),
# so the image never calls HuggingFace Hub at build or runtime.
# Fallback to the hub name lets local dev work without the vendored dir.
_MODEL_DIR = os.path.join(os.path.dirname(__file__), "model", "paraphrase-MiniLM-L3-v2")
EMBEDDING_MODEL = _MODEL_DIR if os.path.isdir(_MODEL_DIR) else "paraphrase-MiniLM-L3-v2"

# Chroma collection names — one per tier
COLLECTION_NAME = "resume_knowledge"          # Tier 1: factual resume (always retrieved)
INTERVIEW_COLLECTION_NAME = "interview_patterns"  # Tier 2: behavioral patterns (RAG-05)
ARCH_COLLECTION_NAME = "system_architecture"      # Arch self-awareness (RAG-06)

# Chunk size for splitting resume text
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Query routing keywords — drive tier-2 / arch inclusion (RAG-05, RAG-06)
ARCH_KEYWORDS = {
    "architecture", "architected", "stack", "tech stack", "how is this built",
    "how is the system built", "how was this built", "deployed", "deployment",
    "infrastructure", "cloud run", "docker", "gemini", "chroma", "rag",
    "embedding model", "vector store", "n8n", "cloud build", "ci/cd",
    "workload identity",
}
INTERVIEW_KEYWORDS = {
    "behavioral", "tell me about a time", "interview", "star method",
    "leadership", "conflict", "mistake", "weakness", "disagreement",
    "prioritize", "ambiguity", "ideal work",
}


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks by character count, respecting line breaks."""
    lines = text.split("\n")
    chunks = []
    current_chunk = ""

    for line in lines:
        # If adding this line would exceed chunk size, save current and start new
        if len(current_chunk) + len(line) + 1 > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Keep overlap from end of previous chunk
            overlap_text = current_chunk[-overlap:] if overlap > 0 else ""
            current_chunk = overlap_text + line + "\n"
        else:
            current_chunk += line + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def needs_interview_tier(question: str) -> bool:
    """Return True when a question matches behavioral/interview keywords (RAG-05)."""
    q = question.lower()
    return any(kw in q for kw in INTERVIEW_KEYWORDS)


def needs_architecture_tier(question: str) -> bool:
    """Return True when a question matches system architecture keywords (RAG-06)."""
    q = question.lower()
    return any(kw in q for kw in ARCH_KEYWORDS)


class ResumeRAG:
    """Manages the multi-tier vector database and retrieval.

    Collections:
      - Tier 1 (self.collection):             factual resume corpus, always queried
      - Tier 2 (self.interview_collection):   mock interview Q&A, queried when
                                              the question matches behavioral keywords
      - Arch (self.arch_collection):          architecture facts, queried when
                                              the question matches architecture keywords
    """

    def __init__(self):
        self._embedder: Optional[SentenceTransformer] = None
        self._client: Optional[chromadb.ClientAPI] = None
        self._collection = None
        self._interview_collection = None
        self._arch_collection = None

    @property
    def embedder(self) -> SentenceTransformer:
        if self._embedder is None:
            logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
            # local_files_only prevents ANY HF Hub metadata calls at load time —
            # critical on Cloud Run where HF rate-limits shared egress IPs and
            # HEAD calls were stalling warm-up indefinitely.
            self._embedder = SentenceTransformer(EMBEDDING_MODEL, local_files_only=True)
        return self._embedder

    @property
    def client(self) -> chromadb.ClientAPI:
        if self._client is None:
            self._client = chromadb.EphemeralClient()
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    @property
    def interview_collection(self):
        if self._interview_collection is None:
            self._interview_collection = self.client.get_or_create_collection(
                name=INTERVIEW_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        return self._interview_collection

    @property
    def arch_collection(self):
        if self._arch_collection is None:
            self._arch_collection = self.client.get_or_create_collection(
                name=ARCH_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        return self._arch_collection

    def _ingest_corpus(self, collection, text: str, id_prefix: str) -> int:
        """Shared helper that chunks, embeds, and stores a corpus into a collection."""
        if collection.count() > 0:
            logger.info(
                "%s already has %d documents, skipping ingest",
                id_prefix, collection.count(),
            )
            return collection.count()
        chunks = chunk_text(text)
        ids = [f"{id_prefix}_{i}" for i in range(len(chunks))]
        embeddings = self.embedder.encode(chunks).tolist()
        collection.add(ids=ids, documents=chunks, embeddings=embeddings)
        logger.info("Ingested %d chunks into %s", len(chunks), id_prefix)
        return len(chunks)

    def ingest(self) -> int:
        """Load resume data, chunk it, embed it, and store in Chroma.
        Returns the number of chunks stored in tier 1 (for backwards compat).
        Also seeds tier-2 and architecture collections.
        """
        tier1_count = self._ingest_corpus(
            self.collection, get_resume_as_text(), "chunk"
        )
        self._ingest_corpus(
            self.interview_collection, get_interview_patterns_as_text(), "iv"
        )
        self._ingest_corpus(
            self.arch_collection, get_adr_content_as_text(), "arch"
        )
        return tier1_count

    def query(self, question: str, top_k: int = 3) -> list[str]:
        """Retrieve the most relevant tier-1 resume chunks for a question.

        Kept for backwards compatibility with existing call sites. Callers that
        want tier-2 or architecture context should use query_all() instead.
        """
        query_embedding = self.embedder.encode([question]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )
        documents = results.get("documents", [[]])[0]
        return documents

    def query_all(self, question: str, top_k: int = 3) -> dict:
        """Unified retrieval across all tiers (RAG-05, RAG-06).

        Always retrieves tier-1 resume chunks. Additionally retrieves tier-2
        interview patterns if the question matches behavioral keywords, and
        architecture content if the question matches arch keywords.

        Returns a dict with:
          - resume_chunks: list[str]
          - interview_chunks: list[str]   (may be empty)
          - arch_chunks: list[str]        (may be empty)
          - top_distance: float           (tier-1 best match distance, for confidence)
          - used_tiers: list[str]         (which tiers contributed; for logging/tests)
        """
        query_embedding = self.embedder.encode([question]).tolist()

        tier1 = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )
        resume_chunks = tier1.get("documents", [[]])[0]
        distances = tier1.get("distances", [[]])[0]
        top_distance = float(distances[0]) if distances else 1.0

        used_tiers = ["resume"]
        interview_chunks: list[str] = []
        arch_chunks: list[str] = []

        if needs_interview_tier(question):
            iv = self.interview_collection.query(
                query_embeddings=query_embedding,
                n_results=top_k,
            )
            interview_chunks = iv.get("documents", [[]])[0]
            if interview_chunks:
                used_tiers.append("interview")

        if needs_architecture_tier(question):
            ar = self.arch_collection.query(
                query_embeddings=query_embedding,
                n_results=top_k,
            )
            arch_chunks = ar.get("documents", [[]])[0]
            if arch_chunks:
                used_tiers.append("architecture")

        return {
            "resume_chunks": resume_chunks,
            "interview_chunks": interview_chunks,
            "arch_chunks": arch_chunks,
            "top_distance": top_distance,
            "used_tiers": used_tiers,
        }


# Module-level singleton — shared across the app
_rag_instance: Optional[ResumeRAG] = None


def get_rag() -> ResumeRAG:
    """Get or create the singleton RAG instance."""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = ResumeRAG()
        _rag_instance.ingest()
    return _rag_instance
