"""
RAG (Retrieval-Augmented Generation) module.
Handles document chunking, embedding, vector storage, and retrieval.
"""

import os
import logging
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from resume_data import get_resume_as_text

logger = logging.getLogger(__name__)

# Embedding model — runs locally, no API key needed
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Chroma collection name
COLLECTION_NAME = "resume_knowledge"

# Where to persist the vector DB (set via env var or default)
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

# Chunk size for splitting resume text
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


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


class ResumeRAG:
    """Manages the resume vector database and retrieval."""

    def __init__(self, persist_dir: str = CHROMA_PERSIST_DIR):
        self.persist_dir = persist_dir
        self._embedder: Optional[SentenceTransformer] = None
        self._client: Optional[chromadb.ClientAPI] = None
        self._collection = None

    @property
    def embedder(self) -> SentenceTransformer:
        if self._embedder is None:
            logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
            self._embedder = SentenceTransformer(EMBEDDING_MODEL)
        return self._embedder

    @property
    def client(self) -> chromadb.ClientAPI:
        if self._client is None:
            self._client = chromadb.Client(ChromaSettings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.persist_dir,
                anonymized_telemetry=False,
            ))
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def ingest(self) -> int:
        """Load resume data, chunk it, embed it, and store in Chroma.
        Returns the number of chunks stored.
        """
        resume_text = get_resume_as_text()
        chunks = chunk_text(resume_text)

        if self.collection.count() > 0:
            logger.info("Collection already has %d documents, skipping ingest", self.collection.count())
            return self.collection.count()

        logger.info("Ingesting %d chunks into vector store", len(chunks))

        ids = [f"chunk_{i}" for i in range(len(chunks))]
        embeddings = self.embedder.encode(chunks).tolist()

        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
        )

        logger.info("Ingested %d chunks successfully", len(chunks))
        return len(chunks)

    def query(self, question: str, top_k: int = 3) -> list[str]:
        """Retrieve the most relevant resume chunks for a question."""
        query_embedding = self.embedder.encode([question]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )

        documents = results.get("documents", [[]])[0]
        return documents


# Module-level singleton — shared across the app
_rag_instance: Optional[ResumeRAG] = None


def get_rag() -> ResumeRAG:
    """Get or create the singleton RAG instance."""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = ResumeRAG()
        _rag_instance.ingest()
    return _rag_instance
