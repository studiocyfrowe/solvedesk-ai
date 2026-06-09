import os
from dotenv import load_dotenv

from solvedesk_cmd.api.startup import MODEL_PATH, CHROMA_DIR, ISSUES_URL

from solvedesk_cmd.infrastructure.vector_database.chroma_store import ChromaStore
from solvedesk_cmd.infrastructure.vector_database.collection_manager import CollectionManager
from solvedesk_cmd.infrastructure.data_context.config_manager import ConfigManager
from solvedesk_cmd.infrastructure.data_context.external_api_source import ExternalApiSource
from solvedesk_cmd.infrastructure.data_context.data_sync_service import DataSyncService
from solvedesk_cmd.infrastructure.generators.ollama import OllamaGenerator
from solvedesk_cmd.infrastructure.installers.require_installer import RequireInstaller
from solvedesk_cmd.infrastructure.transformers.sentence_transformer_provider import SentenceTransformerProvider

from sentence_transformers import SentenceTransformer

load_dotenv()

_model = None
_collection = None

def get_model():
    global _model
    if _model is None:
        _model = load_embedding_model()
    return _model

def get_collection():
    global _collection

    if _collection is None:
        manager = CollectionManager()
        collection_name = os.getenv("COLLECTION_NAME", "random-text")
        _collection = manager.get_collection(collection_name)

    return _collection

def get_embedder():
    return SentenceTransformerProvider(get_model())

def get_vector_store():
    return ChromaStore(get_collection())

def get_chroma_dir() -> str:
    return CHROMA_DIR

def get_collection_name() -> str:
    return os.getenv("COLLECTION_NAME", "random-text")

def get_collection_manager() -> CollectionManager:
    return CollectionManager(
        chroma_dir=get_chroma_dir()
    )
    
def load_embedding_model():
    return SentenceTransformer(MODEL_PATH)

def get_external_api_source(token: str):
    return ExternalApiSource(
        ISSUES_URL,
        token
    )
    
def get_data_sync_service(
    source, 
    embedder, 
    vector_store
):
    return DataSyncService(
        source=source,
        embedder=embedder,
        vector_store=vector_store
    )
    
def get_cli_data_sync_service(
    api_url: str,
    token: str | None = None
):
    model = get_model()

    if model is None:
        raise RuntimeError("Embedding model is not loaded. Check MODEL_PATH in .env.")

    collection = get_collection()
    source = ExternalApiSource(api_url, token)
    embedder = SentenceTransformerProvider(model)
    store = ChromaStore(collection=collection)

    return get_data_sync_service(
        source=source,
        embedder=embedder,
        vector_store=store
    )
    
def get_ollama_generator():
    return OllamaGenerator(
        llm_host=os.getenv('LLM_URL'),
        llm_model=os.getenv('LLM_MODEL')
    )
    
def get_installer():
    return RequireInstaller()

def get_config_manager():
    return ConfigManager()
