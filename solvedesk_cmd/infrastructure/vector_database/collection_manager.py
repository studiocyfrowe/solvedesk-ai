import random
import chromadb
import os

class CollectionManager:
    def __init__(
            self, 
            chroma_dir: str | None = None):
        self.chroma_dir = os.getenv("CHROMA_DIR")
        self.client = chromadb.PersistentClient(
            path=self.chroma_dir
        )

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