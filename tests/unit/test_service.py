from typing import List

from main import const
from main.reindex import ReindexService, Index


def test_valid_index_creation(reindex_service: ReindexService):
    """
    Test valid index creation.
    """
    source_client = reindex_service.source_client
    data: List[Index] = reindex_service.get_all_indexes(client=source_client)

    assert data[0].name == const.ES_TEST_INDEX
    assert data[0].docs_count == 500
