from elasticsearch.helpers import bulk

from elasticsearch_reindex.client import ElasticsearchClient
from elasticsearch_reindex.logger import create_logger

logger = create_logger()


def _get_insert_action(body: dict, es_index: str) -> dict:
    return {"_index": es_index, **body}


def bulk_insert(
    docs: list[dict], es_client: ElasticsearchClient, es_index: str
) -> None:
    """
    Execute insert actions to ElasticSearch.
    """
    actions = [_get_insert_action(body=item, es_index=es_index) for item in docs]
    success, failed = bulk(client=es_client.client, actions=actions, stats_only=True)
    logger.info(f"Bulk insert: success: {success}, failed: {failed}")


def delete_indexes(indexes: list[str], es_client: ElasticsearchClient) -> None:
    """
    Delete specified indexes from ElasticSearch.
    """
    for es_index in indexes:
        es_client.client.indices.delete(index=es_index)
