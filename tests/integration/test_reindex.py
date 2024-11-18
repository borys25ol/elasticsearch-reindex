import pytest

from elasticsearch_reindex import ReindexManager
from elasticsearch_reindex.client import ElasticsearchClient
from tests.conftest import ES_INDEXES_COUNT


@pytest.mark.usefixtures("provide_test_indexes")
def test_valid_data_migration(
    reindex_manager: ReindexManager, elastic_dest_client: ElasticsearchClient
) -> None:
    reindex_manager.start_reindex()
    indexes = elastic_dest_client.get_indexes()
    assert len(indexes) == ES_INDEXES_COUNT
