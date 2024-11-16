from collections.abc import Generator
from datetime import datetime
from time import sleep

import pytest

from elasticsearch_reindex.client import ElasticsearchClient
from elasticsearch_reindex.manager import Manager
from elasticsearch_reindex.reindex import ReindexService
from elasticsearch_reindex.utils import bulk_insert
from tests.config import ES_TEST_INDEX, LOCAL_DEST_HOST, LOCAL_SOURCE_HOST, TEST_ENV

TEST_INDEXES_COUNT = 3
DOCS_COUNT = 10000

DEFAULT_INPUT_PARAMS = {
    "source_host": LOCAL_SOURCE_HOST,
    "dest_host": LOCAL_DEST_HOST,
    "check_interval": 10,
    "concurrent_tasks": 2,
}


@pytest.fixture(autouse=True)
def check_testing_mode():
    """
    Check that testing env was set before each test.
    """
    assert TEST_ENV is True
    yield


@pytest.fixture()
def test_messages() -> list[dict]:
    """
    Return messages with different id.
    """
    return [
        {
            "date": datetime.strptime("August 3, 2021", "%B %d, %Y").isoformat(),
            "id": message_id**2,
            "text": "Some review",
            "source": "amazon",
        }
        for message_id in range(DOCS_COUNT)
    ]


@pytest.fixture()
def reindex_service() -> ReindexService:
    """
    Return initialized reindex service.
    """
    reindex_service = ReindexService(
        source_es_host=LOCAL_SOURCE_HOST, dest_es_host=LOCAL_DEST_HOST
    )
    return reindex_service


@pytest.fixture()
def elastic_client() -> ElasticsearchClient:
    """
    Return initialized reindex service.
    """
    es_client = ElasticsearchClient(
        source_es_host=LOCAL_SOURCE_HOST, dest_es_host=LOCAL_DEST_HOST
    )
    return es_client


@pytest.fixture()
def insert_indexes(
    test_messages: list[dict], elastic_client: ElasticsearchClient
) -> Generator[ReindexService, None, None]:
    """
    Return reindex service.
    """
    for index_number in range(TEST_INDEXES_COUNT):
        es_index = ES_TEST_INDEX.format(number=index_number)
        bulk_insert(
            docs=test_messages,
            es_client=elastic_client.source_client,
            es_index=es_index,
        )
    # Wait some time when data will reach Elasticsearch.
    sleep(2)
    yield elastic_client


@pytest.fixture()
def manager(elastic_client: ElasticsearchClient) -> Generator[Manager, None, None]:
    """
    Return initialized manager class for start reindexing.
    """
    manager_class = Manager.from_dict(data=DEFAULT_INPUT_PARAMS)
    yield manager_class

    # Clear all of test indexes from source ans destination Elastics.
    for index_number in range(TEST_INDEXES_COUNT):
        index = ES_TEST_INDEX.format(number=index_number)
        elastic_client.source_client.indices.delete(index=index)
        elastic_client.dest_client.indices.delete(index=index)
