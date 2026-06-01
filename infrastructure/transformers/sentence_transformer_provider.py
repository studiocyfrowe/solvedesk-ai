from typing import List, Union, Sequence
from domain.ports.embedding_provider import EmbeddingProvider
from sentence_transformers import SentenceTransformer

class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self, model: SentenceTransformer):
        self.model = model

    def embed(self, text: str) -> List[float]:
        emb = self.model.encode(text, convert_to_numpy=True)
        return emb.tolist()
