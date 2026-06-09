from solvedesk_cmd.application.services.builders.env_builder import EnvBuilder
from solvedesk_cmd.application.services.builders.charts_builder import ChartsBuilder
from solvedesk_cmd.application.services.chunks.chunkers import Chunkers
from solvedesk_cmd.application.services.search.search_service import SearchService
from solvedesk_cmd.application.services.data.manage_data_service import ManageDataService
from solvedesk_cmd.application.services.data.data_preprocessor import DataPreprocessor
from solvedesk_cmd.application.services.data.report_data import DataReporter
from solvedesk_cmd.application.services.factories.metadata_factory import MetadataFactory
from solvedesk_cmd.application.services.factories.record_factory import RecordFactory

def get_env_builder():
    return EnvBuilder()

def get_chart_builder():
    return ChartsBuilder()

def get_metadata_factory():
    return MetadataFactory()

def get_record_factory():
    return RecordFactory()

def get_chunker(
    ids,
    documents,
    metadatas,
    model,
    target_collection,
    chunk_size
):
    return Chunkers(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        model=model,
        target_collection=target_collection,
        chunk_size=chunk_size
    )

def get_data_reporter(
    model,
    documents,
    embeddings,
    clusters
):
    return DataReporter(
        model=model,
        documents=documents,
        embeddings=embeddings,
        clusters=clusters
    )

def get_search_service(
    embedder,
    vector_store
):
    return SearchService(
        embedder=embedder,
        store=vector_store
    )
    
def get_manage_data_service(
    embedder,
    vector_store
):
    return ManageDataService(
        embedder=embedder,
        store=vector_store
    )
    
def get_data_preprocessor(
    records: list[dict],
    required_fields: list[str],
    text_fields: list[str],
    min_words: int = 3
):
    return DataPreprocessor(
        records=records,
        required_fields=required_fields,
        text_fields=text_fields,
        min_words=min_words
    )