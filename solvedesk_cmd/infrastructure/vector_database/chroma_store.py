from typing import Dict, Any
from solvedesk_cmd.domain.ports.vector_store import VectorStore

class ChromaStore(VectorStore):
    def __init__(self, collection):
        self.collection = collection

    def search(self, vector: list[float], top_k: int):
        return self.collection.query(
            query_embeddings=[vector],
            n_results=top_k
        )

    def get_single(self, issue_id: int):
        return self.collection.get(
            ids=[str(issue_id)]
        )

    def add_new(
        self,
        doc_id: str,
        embedding: list[float],
        document: str,
        metadata: Dict[str, Any]
    ):
        return self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata]
        )

    def update_single_issue(
        self,
        doc_id: str,
        embedding: list[float],
        document: str,
        metadata: Dict[str, Any]
    ):
        return self.collection.update(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata]
        )

    def delete_single_issue(self, issue_id: int):
        return self.collection.delete(
            ids=[str(issue_id)]
        )