from elasticsearch import Elasticsearch, exceptions

from elasticsearch_reindex.const import DEFAULT_ES_KWARGS
from elasticsearch_reindex.errors import (
    ES_NODE_NOT_FOUND_ERROR,
    ElasticSearchNodeNotFoundException,
)
from elasticsearch_reindex.schema import Config, HttpAuth, Index
from elasticsearch_reindex.utils import chunkify


class ElasticsearchClient:
    """
    Client for manipulation with Elasticsearch clients and indexes.
    """

    def __init__(self, config: Config) -> None:
        self.config = config

    @property
    def source_client(self) -> Elasticsearch:
        """
        Return Elasticsearch client where data will be transferred from.
        """
        return self._get_es_client(
            es_host=self.config.source_host, es_http_auth=self.config.http_auth_source
        )

    @property
    def dest_client(self) -> Elasticsearch:
        """
        Return Elasticsearch client where data will be transferred.
        """
        return self._get_es_client(
            es_host=self.config.dest_host, es_http_auth=self.config.http_auth_dest
        )

    def get_source_indexes(self) -> list[Index]:
        """
        Return all indexes in Elasticsearch and amount of documents.
        """
        indexes = self.source_client.cat.indices(h="index,docs.count", s="index")
        return self._get_all_indexes(indexes=indexes.split())

    def get_dest_indexes(self) -> list[Index]:
        """
        Return all indexes in Elasticsearch and amount of documents.
        """
        indexes = self.dest_client.cat.indices(h="index,docs.count", s="index")
        return self._get_all_indexes(indexes=indexes.split())

    @staticmethod
    def get_user_indexes(
        source_indexes: list[Index], user_indexes: list[str]
    ) -> list[Index]:
        """
        Compare indexes provided by user.
        Return indexes for migration.

        :param source_indexes: List of source indexes.
        :param user_indexes: List of user indexes.
        :return: List of `Index` objects.
        """
        return [index for index in source_indexes if index.name in set(user_indexes)]

    @staticmethod
    def _get_es_client(es_host: str, es_http_auth: HttpAuth | None) -> Elasticsearch:
        """
        Ping ElasticSearch server and return initialized client object.
        """
        client = Elasticsearch(hosts=es_host, **DEFAULT_ES_KWARGS)
        try:
            client.info()
        except exceptions.ConnectionError:
            raise ElasticSearchNodeNotFoundException(
                message=ES_NODE_NOT_FOUND_ERROR.format(host=es_host)
            )
        except Exception as e:
            raise ElasticSearchNodeNotFoundException(
                message=ES_NODE_NOT_FOUND_ERROR.format(host=f"{es_host}, error: {e}")
            )
        return client

    @staticmethod
    def _get_all_indexes(indexes: list[str]) -> list[Index]:
        """
        Return all indexes in Elasticsearch and amount of documents.
        """
        return [
            Index(name=name, docs_count=int(count))
            for name, count in chunkify(lst=indexes, n=2)
            if not name.startswith(".")
        ]
