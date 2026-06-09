from abc import ABC, abstractmethod
from typing import List, Dict, Any

class VectorStore(ABC):
    @abstractmethod
    def search(self, vector: list[float], top_k: int):
        pass

    @abstractmethod
    def get_single(self, issue_id: int):
        pass

    @abstractmethod
    def add_new(self, doc_id: str, embedding: list[float], document: str, metadata: Dict[str, Any]):
        pass

    @abstractmethod
    def update_single_issue(self, doc_id: str, embedding: list[float], document: str, metadata: Dict[str, Any]):
        pass

    @abstractmethod
    def delete_single_issue(self, issue_id: int):
        pass