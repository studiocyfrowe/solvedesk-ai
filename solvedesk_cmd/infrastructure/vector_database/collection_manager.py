import random
import chromadb
import os
from dotenv import load_dotenv


class CollectionManager:
    def __init__(self):
        self.client = self._create_client()

    def _create_client(self):
        load_dotenv(override=True)

        chroma_dir = os.getenv("CHROMA_DIR")

        if not chroma_dir:
            raise ValueError("CHROMA_DIR is not configured in .env")

        return chromadb.PersistentClient(
            path=chroma_dir
        )

    def refresh(self):
        self.client = self._create_client()

    def get_collection(self, collection_name: str):
        collection = self.client.get_collection(
            name=collection_name
        )
        
        data = collection.get(
            include=["documents", "metadatas"]
        )
        
        ids = data.get("ids", [])
        documents = data.get("documents", [])
        metadatas = data.get("metadatas", [])
        
        return ids, documents, metadatas, collection

    def list_all(self) -> list[dict]:
        collections = self.client.list_collections()

        result = []

        for collection in collections:
            full_collection = self.client.get_collection(
                name=collection.name
            )

            result.append({
                "name": full_collection.name,
                "id": full_collection.id,
                "metadata": full_collection.metadata,
                "documents_count": full_collection.count()
            })

        return result

    def retrieve_details(self, collection_name: str) -> dict:
        collection = self.client.get_collection(
            name=collection_name
        )

        data = collection.get(
            include=["documents", "metadatas"]
        )

        return {
            "id": collection.id,
            "name": collection.name,
            "metadata": collection.metadata,
            "documents_count": collection.count(),
            "documents": data.get("documents", []),
            "metadatas": data.get("metadatas", [])
        }

    def create(self, collection_name: str | None = None) -> str:
        if not collection_name:
            random_id = random.randint(1000, 9999)
            collection_name = f"sd-collection-{random_id}"

        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        return collection.name

    def delete(self, collection_name: str) -> bool:
        try:
            self.client.delete_collection(
                name=collection_name
            )
            return True
        except Exception:
            return False