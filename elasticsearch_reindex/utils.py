from collections.abc import Iterable

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from elasticsearch_reindex.logs import create_logger
from elasticsearch_reindex.schema import Index

logger = create_logger(__name__)


def chunkify(lst: list, n: int) -> Iterable:
    """
    Yield successive n-sized chunks from list.
    """
    # Slice needs for bypass black failing.
    yield from (lst[slice(i, i + n)] for i in range(0, len(lst), n))


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
    logger.info(f"Successfully actions: {success}. Failed actions: {failed}")


def get_flatten_dict(data: list[Index]) -> dict:
    """
    Convert list of dataclasses to dict for fast searching.
    """
    return {index.name: index.docs_count for index in data}


def check_migrated_indexes(
    source_indexes: list[Index], dest_indexes: list[Index]
) -> tuple[list, list]:
    """
    Check if index from `source_indexes` exist in `dest_indexes`.
    If index already exist we should check if all documents was transferred.
    """
    source_indexes = get_flatten_dict(data=source_indexes)
    dest_indexes = get_flatten_dict(data=dest_indexes)

    not_migrated, partial_migrated = [], []

    for index, docs_count in source_indexes.items():
        if dest_indexes.get(index):
            if docs_count != dest_indexes[index]:
                partial_migrated.append(index)
        else:
            not_migrated.append(index)

    return not_migrated, partial_migrated
