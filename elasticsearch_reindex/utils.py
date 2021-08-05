from typing import Iterable, List

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from elasticsearch_reindex.logs import create_logger

logger = create_logger(__name__)


def chunkify(lst: List, n: int) -> Iterable:
    """
    Yield successive n-sized chunks from list.
    """
    # Slice needs for bypass black failing.
    yield from (lst[slice(i, i + n)] for i in range(0, len(lst), n))


def _get_insert_action(body: dict, es_index: str) -> dict:
    return {
        "_index": es_index,
        **body,
    }


def bulk_insert(docs: List[dict], es_client: Elasticsearch, es_index: str):
    """
    Execute insert actions to ElasticSearch.

    :param docs: List with document to insert.
    :param es_client: ElasticSearch initialized client.
    :param es_index: ElasticSearch index where data will be inserted.
    """
    actions = [_get_insert_action(body=item, es_index=es_index) for item in docs]

    success, failed = bulk(client=es_client, actions=actions, stats_only=True)

    logger.info(f"Successfully actions: {success}. Failed actions: {failed}")
