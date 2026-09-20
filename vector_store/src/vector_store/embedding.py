"""Embedding via a local llama.cpp server (OpenAI-compatible /v1/embeddings)."""
import os

import requests

LLAMACPP_URL = os.environ.get("LLAMACPP_URL", "http://localhost:8080")

# nomic-embed-text-v1.5 requires these task prefixes to get good results -
# skipping them is the most common mistake with this model.
DOCUMENT_PREFIX = "search_document: "
QUERY_PREFIX = "search_query: "


def _embed(text: str) -> list[float]:
    resp = requests.post(
        f"{LLAMACPP_URL}/v1/embeddings",
        json={"input": text},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"][0]["embedding"]


def embed_document(text: str) -> list[float]:
    return _embed(DOCUMENT_PREFIX + text)


def embed_query(text: str) -> list[float]:
    return _embed(QUERY_PREFIX + text)
