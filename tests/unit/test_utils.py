from elasticsearch_reindex.schema import Index
from elasticsearch_reindex.utils import check_migrated_indexes, chunkify


def test_chunkify():
    lst = [1, 2, 3, 4, 5, 6]
    n = 2
    chunks = list(chunkify(lst, n))
    assert len(chunks) == 3
    assert chunks == [[1, 2], [3, 4], [5, 6]]

    # Test edge case: empty list
    lst = []
    chunks = list(chunkify(lst, n))
    assert not len(chunks)

    # Test edge case: chunk size larger than list
    lst = [1, 2, 3]
    chunks = list(chunkify(lst, 5))
    assert chunks == [[1, 2, 3]]


def test_check_migrated_indexes():
    source_indexes = [
        Index(name="index1", docs_count=100),
        Index(name="index2", docs_count=200),
        Index(name="index3", docs_count=300),
    ]
    dest_indexes = [
        Index(name="index1", docs_count=100),
        Index(name="index2", docs_count=150),  # Partial migration
    ]

    not_migrated, partial_migrated = check_migrated_indexes(
        source_indexes, dest_indexes
    )

    assert not_migrated == ["index3"]
    assert partial_migrated == ["index2"]

    # Test case: all indexes migrated
    dest_indexes = [
        Index(name="index1", docs_count=100),
        Index(name="index2", docs_count=200),
        Index(name="index3", docs_count=300),
    ]
    not_migrated, partial_migrated = check_migrated_indexes(
        source_indexes, dest_indexes
    )
    assert not len(not_migrated)
    assert not len(partial_migrated)

    # Test case: no indexes migrated
    dest_indexes = []
    not_migrated, partial_migrated = check_migrated_indexes(
        source_indexes, dest_indexes
    )
    assert not_migrated == ["index1", "index2", "index3"]
    assert not len(partial_migrated)
