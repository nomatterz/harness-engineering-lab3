import os

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "lab3")
VECTOR_SIZE = int(os.environ.get("VECTOR_SIZE", "768"))


class QdrantBackend:
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL)
        self._ensure_collection()

    def _ensure_collection(self):
        if not self.client.collection_exists(COLLECTION_NAME):
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=qmodels.VectorParams(
                    size=VECTOR_SIZE, distance=qmodels.Distance.COSINE
                ),
            )

    def upsert(self, id: str, vector: list[float], payload: dict) -> None:
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[qmodels.PointStruct(id=id, vector=vector, payload=payload)],
        )

    def search(self, vector: list[float], top_k: int = 5) -> list[dict]:
        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=top_k,
        ).points
        return [
            {"id": r.id, "score": r.score, "payload": r.payload} for r in results
        ]
