import pytest
from elasticsearch import Elasticsearch

from elasticsearch_reindex.client import ElasticsearchClient
from elasticsearch_reindex.errors import ElasticSearchNodeNotFoundException
from elasticsearch_reindex.schema import Index
from tests.conftest import ES_INDEXES_COUNT

INVALID_SOURCE_HOST = "http://127.0.0.1:9900"
INVALID_DEST_HOST = "http://127.0.0.1:9901"


def test_invalid_es_connection():
    with pytest.raises(ElasticSearchNodeNotFoundException):
        es_client = ElasticsearchClient(es_host=INVALID_SOURCE_HOST, http_auth=None)
        assert isinstance(es_client.client, Elasticsearch)


def test_valid_es_connection(elastic_source_client: ElasticsearchClient):
    assert isinstance(elastic_source_client.client, Elasticsearch)


@pytest.mark.usefixtures("provide_test_source_indexes")
def test_valid_indexes_creation(elastic_source_client: ElasticsearchClient) -> None:
    data: list[Index] = elastic_source_client.get_indexes()
    assert len(data) == ES_INDEXES_COUNT
