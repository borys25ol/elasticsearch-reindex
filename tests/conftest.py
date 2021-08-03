from datetime import datetime
from time import sleep

import pytest

from main import const
from main.reindex import ReindexService
from main.utils import bulk_insert


@pytest.fixture()
def test_messages():
    """
    Return 500 messages with different id.
    """
    return [
        {
            "date": datetime.strptime("August 3, 2021", "%B %d, %Y").isoformat(),
            "id": message_id ** 2,
            "text": "Some review",
            "source": "walmart",
            "_meta": {"ES_INDEX": const.ES_TEST_INDEX},
        }
        for message_id in range(500)
    ]


@pytest.fixture()
def reindex_service(test_messages):
    """
    Return rei.
    """
    reindex = ReindexService(
        source_es_host="localhost:9201", dest_es_host="localhost:9202"
    )

    bulk_insert(
        docs=test_messages,
        es_client=reindex.source_client,
        es_index=const.ES_TEST_INDEX,
    )

    # Wait some time when data will reach Elasticsearch.
    sleep(2)

    yield reindex

    reindex.source_client.indices.delete(index=const.ES_TEST_INDEX)
