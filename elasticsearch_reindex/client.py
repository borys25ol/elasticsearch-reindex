from elasticsearch import Elasticsearch, exceptions

from elasticsearch_reindex.errors import (
    ES_NODE_NOT_FOUND_ERROR,
    ElasticSearchNodeNotFoundException,
)
from elasticsearch_reindex.schema import ElasticsearchConfig, HttpAuth, Index
from elasticsearch_reindex.utils import chunkify


class ElasticsearchClient:
    """
    Client for manipulation with Elasticsearch clients and indexes.
    """

    settings = {"max_retries": 3, "request_timeout": 30, "retry_on_timeout": False}

    def __init__(self, es_host: str, http_auth: HttpAuth | None) -> None:
        self._http_auth = http_auth
        self._client = self._prepare_es_client(
            es_host=es_host, es_http_auth=self.http_auth
        )

    @classmethod
    def from_config(cls, config: ElasticsearchConfig) -> "ElasticsearchClient":
        """
        Initialize ElasticsearchClient from ElasticsearchConfig object.
        """
        return cls(es_host=config.host, http_auth=config.http_auth)

    @property
    def client(self) -> Elasticsearch:
        """
        Return prepared Elasticsearch client.
        """
        return self._client

    @property
    def http_auth(self) -> tuple[str, str] | None:
        """
        Return HTTP auth credentials if provided.
        """
        return self._http_auth.as_tuple() if self._http_auth else None

    def get_indexes(self) -> list[Index]:
        """
        Return all Elasticsearch indexes and amount of documents.
        """
        indexes = self.client.cat.indices(h="index,docs.count", s="index")
        return self._parse_indexes(indexes=indexes.split())

    def _prepare_es_client(
        self, es_host: str, es_http_auth: tuple[str, str] | None = None
    ) -> Elasticsearch:
        """
        Ping ElasticSearch server and return initialized client object.
        """
        client = Elasticsearch(hosts=es_host, basic_auth=es_http_auth, **self.settings)
        try:
            client.info()
        except exceptions.ConnectionError:
            raise ElasticSearchNodeNotFoundException(
                ES_NODE_NOT_FOUND_ERROR.format(host=es_host)
            )
        except Exception as e:
            raise ElasticSearchNodeNotFoundException(
                ES_NODE_NOT_FOUND_ERROR.format(host=f"{es_host}, error: {e}")
            )

        return client

    @staticmethod
    def _parse_indexes(indexes: list[str]) -> list[Index]:
        """
        Return all indexes in Elasticsearch and amount of documents.
        """
        return [
            Index(name=name, docs_count=int(count))
            for name, count in chunkify(lst=indexes, n=2)
            if not name.startswith(".")
        ]
