from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from elasticsearch_reindex.logger import create_logger

logger = create_logger()


def _get_insert_action(body: dict, es_index: str) -> dict:
    return {"_index": es_index, **body}


def bulk_insert(docs: list[dict], es_client: Elasticsearch, es_index: str) -> None:
    """
    Execute insert actions to ElasticSearch.

    :param docs: List with document to insert.
    :param es_client: ElasticSearch initialized client.
    :param es_index: ElasticSearch index where data will be inserted.
    """
    actions = [_get_insert_action(body=item, es_index=es_index) for item in docs]
    success, failed = bulk(client=es_client, actions=actions, stats_only=True)
    logger.info(f"Bulk insert: success: {success}, failed: {failed}")
