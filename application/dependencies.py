from application.services.builders.env_builder import EnvBuilder
from application.services.search.search_service import SearchService
from application.services.data.manage_data_service import ManageDataService
from application.services.data.data_preprocessor import DataPreprocessor
from application.services.data.report_data import DataReporter
from application.services.factories.metadata_factory import MetadataFactory
from application.services.factories.record_factory import RecordFactory
from application.services.builders.charts_builder import ChartsBuilder

def get_env_builder():
    return EnvBuilder()

def get_chart_builder():
    return ChartsBuilder()

def get_metadata_factory():
    return MetadataFactory()

def get_record_factory():
    return RecordFactory()

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