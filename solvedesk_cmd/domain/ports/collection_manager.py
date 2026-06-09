from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any

class CollectionManager(ABC):
    @abstractmethod
    def list_all() -> list:
        pass

    @abstractmethod
    def retrieve_details(collection_name: str) -> dict:
        pass

    @abstractmethod
    def create(
        chroma_dir: str | Path,
        collection_name: str | None = None
    ) -> bool:
        pass

    @abstractmethod
    def delete(collection_name: str) -> bool:
        pass