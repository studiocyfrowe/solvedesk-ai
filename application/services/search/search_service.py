from domain.ports.embedding_provider import EmbeddingProvider
from domain.ports.vector_store import VectorStore

class SearchService:
    def __init__(self, embedder: EmbeddingProvider, store: VectorStore):
        self.embedder = embedder
        self.store = store

    def search(self, query: str, top_k: int):
        emb = self.embedder.embed(query)
        return self.store.search(emb, top_k)