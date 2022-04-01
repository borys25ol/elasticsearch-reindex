from typing import List

import pytest
from elasticsearch import Elasticsearch

from elasticsearch_reindex import Manager
from elasticsearch_reindex.client import ElasticsearchClient
from elasticsearch_reindex.errors import ElasticSearchNodeNotFoundException
from elasticsearch_reindex.schema import Index
from tests.conftest import TEST_INDEXES_COUNT

INVALID_SOURCE_HOST = "localhost:9900"
INVALID_DEST_HOST = "localhost:9901"


def test_invalid_es_connection() -> None:
    """
    Test valid Elasticsearch client initialization.
    """
    es_client = ElasticsearchClient(
        source_es_host=INVALID_SOURCE_HOST, dest_es_host=INVALID_DEST_HOST
    )
    with pytest.raises(ElasticSearchNodeNotFoundException):
        assert isinstance(es_client.source_client, Elasticsearch)

    with pytest.raises(ElasticSearchNodeNotFoundException):
        assert isinstance(es_client.dest_client, Elasticsearch)


def test_valid_es_connection(elastic_client: ElasticsearchClient) -> None:
    """
    Test valid Elasticsearch client initialization.
    """
    assert isinstance(elastic_client.source_client, Elasticsearch)
    assert isinstance(elastic_client.dest_client, Elasticsearch)


def test_valid_indexes_creation(
    insert_indexes, elastic_client: ElasticsearchClient
) -> None:
    """
    Test valid indexes creation.
    """
    data: List[Index] = elastic_client.get_source_indexes()
    assert len(data) == TEST_INDEXES_COUNT


def test_valid_data_migration(
    manager: Manager, elastic_client: ElasticsearchClient
) -> None:
    """
    Test successfully reindexing.
    """
    manager.start_reindex()
    indexes = elastic_client.get_dest_indexes()
    assert len(indexes) == TEST_INDEXES_COUNT
