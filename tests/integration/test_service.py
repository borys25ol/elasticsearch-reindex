from typing import List

import pytest
from elasticsearch import Elasticsearch

from elasticsearch_reindex.errors import ElasticSearchNodeNotFoundException
from elasticsearch_reindex.reindex import Index, ReindexService
from tests.conftest import TEST_INDEXES_COUNT

INVALID_SOURCE_HOST = "localhost:9900"
INVALID_DEST_HOST = "localhost:9901"


def test_invalid_es_connection():
    """
    Test valid Elasticsearch client initialization.
    """
    reindex_service = ReindexService(
        source_es_host=INVALID_SOURCE_HOST, dest_es_host=INVALID_DEST_HOST
    )
    with pytest.raises(ElasticSearchNodeNotFoundException):
        assert isinstance(reindex_service.source_client, Elasticsearch)

    with pytest.raises(ElasticSearchNodeNotFoundException):
        assert isinstance(reindex_service.dest_client, Elasticsearch)


def test_valid_es_connection(reindex_service: ReindexService):
    """
    Test valid Elasticsearch client initialization.
    """
    assert isinstance(reindex_service.source_client, Elasticsearch)


def test_valid_indexes_creation(insert_indexes, reindex_service):
    """
    Test valid indexes creation.
    """
    source_client = reindex_service.source_client
    data: List[Index] = reindex_service.get_all_indexes(client=source_client)

    assert len(data) == TEST_INDEXES_COUNT


def test_valid_data_migration(manager, reindex_service):
    """
    Test successfully reindexing.
    """
    dest_client = reindex_service.dest_client
    indexes = reindex_service.get_all_indexes(client=dest_client)

    assert len(indexes) == TEST_INDEXES_COUNT
