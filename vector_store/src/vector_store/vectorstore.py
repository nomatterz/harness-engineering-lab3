"""Backend-agnostic vector store interface.

The MCP server and the indexing script both talk to this interface, not to a
specific database's client library. Swapping the backing store means adding
one new class under backends/ that implements this protocol - nothing else
changes.
"""
from typing import Protocol


class SearchResult(dict):
    """A single match: {"id": ..., "score": ..., "payload": {...}}."""


class VectorStore(Protocol):
    def upsert(self, id: str, vector: list[float], payload: dict) -> None:
        """Store one vector + its associated data."""
        ...

    def search(self, vector: list[float], top_k: int = 5) -> list[SearchResult]:
        """Return the top_k most similar stored items."""
        ...


def get_backend() -> VectorStore:
    import os

    backend = os.environ.get("VECTOR_BACKEND", "qdrant")
    if backend == "qdrant":
        from .backends.qdrant_backend import QdrantBackend

        return QdrantBackend()
    raise ValueError(f"Unknown VECTOR_BACKEND: {backend}")
