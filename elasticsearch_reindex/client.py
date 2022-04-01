from typing import List

from elasticsearch import Elasticsearch, exceptions

from elasticsearch_reindex.const import DEFAULT_ES_KWARGS
from elasticsearch_reindex.errors import (
    ES_NODE_NOT_FOUND_ERROR,
    ElasticSearchNodeNotFoundException,
)
from elasticsearch_reindex.schema import Index
from elasticsearch_reindex.utils import chunkify


class ElasticsearchClient:
    """
    Client for manipulation with Elasticsearch clients and indexes.
    """

    def __init__(self, source_es_host: str, dest_es_host: str) -> None:
        self.source_es_host = source_es_host
        self.dest_es_host = dest_es_host

    @property
    def source_client(self) -> Elasticsearch:
        """
        Return Elasticsearch client where data will be transferred from.
        """
        return self._get_es_client(es_host=self.source_es_host)

    @property
    def dest_client(self) -> Elasticsearch:
        """
        Return Elasticsearch client where data will be transferred.
        """
        return self._get_es_client(es_host=self.dest_es_host)

    def get_source_indexes(self) -> List[Index]:
        """
        Return all indexes in Elasticsearch and amount of documents.
        """
        indexes = self.source_client.cat.indices(h="index,docs.count", s="index")
        return self._get_all_indexes(indexes=indexes.split())

    def get_dest_indexes(self) -> List[Index]:
        """
        Return all indexes in Elasticsearch and amount of documents.
        """
        indexes = self.dest_client.cat.indices(h="index,docs.count", s="index")
        return self._get_all_indexes(indexes=indexes.split())

    @staticmethod
    def get_user_indexes(
        source_indexes: List[Index], user_indexes: List[str]
    ) -> List[Index]:
        """
        Compare indexes provided by user.
        Return indexes for migration.

        :param source_indexes: List of source indexes.
        :param user_indexes: List of user indexes.
        :return: List of `Index` objects.
        """
        return [index for index in source_indexes if index.name in set(user_indexes)]

    @staticmethod
    def _get_es_client(es_host: str) -> Elasticsearch:
        """
        Ping ElasticSearch server and return initialized client object.
        """
        client = Elasticsearch(hosts=es_host, **DEFAULT_ES_KWARGS)  # type: ignore
        try:
            client.info()
        except exceptions.ConnectionError:
            raise ElasticSearchNodeNotFoundException(
                message=ES_NODE_NOT_FOUND_ERROR.format(host=es_host)
            )
        return client

    @staticmethod
    def _get_all_indexes(indexes: List[str]) -> List[Index]:
        """
        Return all indexes in Elasticsearch and amount of documents.
        """
        return [
            Index(name=name, docs_count=int(count))
            for name, count in chunkify(lst=indexes, n=2)
            if not name.startswith(".")
        ]
