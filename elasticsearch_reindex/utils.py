from collections.abc import Iterable

from elasticsearch_reindex.logger import create_logger
from elasticsearch_reindex.schema import Index

logger = create_logger()


def chunkify(lst: list, n: int) -> Iterable:
    """
    Yield successive n-sized chunks from list.
    """
    # Slice needs for bypass black failing.
    yield from (lst[slice(i, i + n)] for i in range(0, len(lst), n))


def _get_flatten_dict(data: list[Index]) -> dict:
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
    source_indexes = _get_flatten_dict(data=source_indexes)
    dest_indexes = _get_flatten_dict(data=dest_indexes)

    not_migrated, partial_migrated = [], []

    for index, docs_count in source_indexes.items():
        if dest_indexes.get(index):
            if docs_count != dest_indexes[index]:
                partial_migrated.append(index)
        else:
            not_migrated.append(index)

    return not_migrated, partial_migrated
