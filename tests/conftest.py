from datetime import datetime
from time import sleep

import pytest

from elasticsearch_reindex import const
from elasticsearch_reindex.manager import Manager
from elasticsearch_reindex.reindex import ReindexService
from elasticsearch_reindex.utils import bulk_insert

TEST_INDEXES_COUNT = 3
DOCS_COUNT = 10000

DEFAULT_INPUT_PARAMS = {
    "source_host": const.LOCAL_SOURCE_HOST,
    "dest_host": const.LOCAL_DEST_HOST,
    "check_interval": 10,
    "concurrent_tasks": 2,
}


@pytest.fixture()
def test_messages():
    """
    Return messages with different id.
    """
    return [
        {
            "date": datetime.strptime("August 3, 2021", "%B %d, %Y").isoformat(),
            "id": message_id ** 2,
            "text": "Some review",
            "source": "amazon",
        }
        for message_id in range(DOCS_COUNT)
    ]


@pytest.fixture()
def reindex_service():
    """
    Return initialized reindex service.
    """
    reindex_service = ReindexService(
        source_es_host=const.LOCAL_SOURCE_HOST, dest_es_host=const.LOCAL_DEST_HOST
    )
    return reindex_service


@pytest.fixture()
def insert_indexes(test_messages, reindex_service: ReindexService):
    """
    Return reindex service.
    """
    for index_number in range(TEST_INDEXES_COUNT):
        es_index = const.ES_TEST_INDEX.format(number=index_number)
        bulk_insert(
            docs=test_messages,
            es_client=reindex_service.source_client,
            es_index=es_index,
        )

    # Wait some time when data will reach Elasticsearch.
    sleep(2)

    yield reindex_service


@pytest.fixture()
def manager(reindex_service: ReindexService):
    """
    Return initialized manager class for start reindexing.
    """
    manager_class = Manager.from_dict(data=DEFAULT_INPUT_PARAMS)
    manager_class.start_reindex()

    yield

    # Clear all of test indexes from source ans destination Elastics.
    for index_number in range(TEST_INDEXES_COUNT):
        index = const.ES_TEST_INDEX.format(number=index_number)
        reindex_service.source_client.indices.delete(index=index)
        reindex_service.dest_client.indices.delete(index=index)
