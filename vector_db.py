# vector_db.py

import qdrant_client
from qdrant_client.http.models import Distance, VectorParams
from .config import config

class VectorDB:
    def __init__(self):
        self.client = qdrant_client.QdrantClient(host=config.vector_db_host, port=config.vector_db_port)
        self.collection_name = "mathlib_lemmas"

    def init_collection(self, vector_size: int = 768):
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    def add_lemma(self, lemma: str, embedding: List[float]):
        self.client.upsert(
            collection_name=self.collection_name,
            points=[{
                "id": hash(lemma) % 2**63,
                "vector": embedding,
                "payload": {"text": lemma}
            }]
        )

    def search(self, query: str, embedding: List[float], top_k: int = 10):
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            limit=top_k,
        )
        return [hit.payload["text"] for hit in results]