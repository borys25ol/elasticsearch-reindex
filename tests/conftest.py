import os
from collections.abc import Generator
from datetime import datetime
from time import sleep

import pytest

from elasticsearch_reindex.client import ElasticsearchClient
from elasticsearch_reindex.manager import ReindexManager
from elasticsearch_reindex.reindex import ReindexService
from elasticsearch_reindex.schema import Config
from tests.utils import bulk_insert, delete_indexes

ES_INDEXES_COUNT = 3
ES_INDEX_DOCS_COUNT = 10000
ES_INDEX_TEMPLATE = "test_index_{number}"


@pytest.fixture(autouse=True)
def check_testing_mode():
    """
    Check that testing env was set before each test.
    """
    assert os.getenv("ENV") == "test"
    yield


@pytest.fixture
def config() -> Config:
    """
    Return initialized config.
    """
    es_host = os.getenv("LOCAL_IP")
    es_source_port = os.getenv("ES_SOURCE_PORT")
    es_dest_port = os.getenv("ES_DEST_PORT")
    return Config(
        source_host=f"http://{es_host}:{es_source_port}",
        source_http_auth=None,
        dest_host=f"http://{es_host}:{es_dest_port}",
        dest_http_auth=None,
        indexes=[],
    )


@pytest.fixture
def test_messages() -> list[dict]:
    """
    Return messages with different id.
    """
    return [
        {
            "id": message_id**2,
            "date": datetime(year=2024, month=11, day=18).isoformat(),
            "title": "Some title",
            "text": "Some review",
            "source": "some-data-source",
        }
        for message_id in range(ES_INDEX_DOCS_COUNT)
    ]


@pytest.fixture
def reindex_service(config: Config) -> ReindexService:
    """
    Return initialized reindex service.
    """
    return ReindexService(config=config)


@pytest.fixture
def elastic_source_client(config: Config) -> ElasticsearchClient:
    """
    Return initialized source Elasticsearch client.
    """
    return ElasticsearchClient(
        es_host=config.source_host, http_auth=config.http_auth_source
    )


@pytest.fixture
def elastic_dest_client(config: Config) -> ElasticsearchClient:
    """
    Return initialized destination Elasticsearch client.
    """
    return ElasticsearchClient(
        es_host=config.dest_host, http_auth=config.http_auth_dest
    )


@pytest.fixture
def reindex_manager(
    config: Config,
    elastic_source_client: ElasticsearchClient,
    elastic_dest_client: ElasticsearchClient,
) -> ReindexManager:
    """
    Return initialized manager class for start reindexing.
    """
    return ReindexManager(config=config)


@pytest.fixture
def test_indexes() -> list[str]:
    return [ES_INDEX_TEMPLATE.format(number=num) for num in range(ES_INDEXES_COUNT)]


@pytest.fixture
def provide_test_source_indexes(
    elastic_source_client: ElasticsearchClient,
    test_indexes: list[str],
    test_messages: list[dict],
) -> Generator[ReindexService, None, None]:
    """
    Insert test indexes with data to source Elasticsearch node.
    """
    for es_index in test_indexes:
        bulk_insert(
            docs=test_messages, es_client=elastic_source_client, es_index=es_index
        )
    # Wait some time when data will reach Elasticsearch.
    sleep(2)
    yield

    # Clear all test indexes from source and destination Elasticsearch nodes.
    delete_indexes(indexes=test_indexes, es_client=elastic_source_client)


@pytest.fixture
def provide_test_indexes(
    elastic_source_client: ElasticsearchClient,
    elastic_dest_client: ElasticsearchClient,
    test_indexes: list[str],
    test_messages: list[dict],
) -> Generator[ReindexService, None, None]:
    """
    Insert test indexes with data to source Elasticsearch node.
    """
    for es_index in test_indexes:
        bulk_insert(
            docs=test_messages, es_client=elastic_source_client, es_index=es_index
        )
    # Wait some time when data will reach Elasticsearch.
    sleep(2)
    yield

    # Clear all test indexes from source and destination Elasticsearch nodes.
    delete_indexes(indexes=test_indexes, es_client=elastic_source_client)
    delete_indexes(indexes=test_indexes, es_client=elastic_dest_client)
