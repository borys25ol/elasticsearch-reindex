from dataclasses import dataclass
from typing import List

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError

from main.errors import ElasticSearchNodeNotFoundException, ES_NODE_NOT_FOUND_ERROR
from main.utils import chunkify


@dataclass
class Index:
    """
    Dataclass for storing ES index cat data.
    """

    name: str
    docs_count: int


class ReindexService:
    """
    This class provide simple interface to ElasticSearch reindex API.
    """

    def __init__(self, source_es_host: str, dest_es_host: str):
        self.source_es_host = source_es_host
        self.dest_es_host = dest_es_host

    @property
    def source_client(self):
        """
        Return Elasticsearch client where data will be transferred from.
        """
        return self._get_es_client(es_host=self.source_es_host)

    @property
    def dest_client(self):
        """
        Return Elasticsearch client where data will be transferred.
        """
        return self._get_es_client(es_host=self.dest_es_host)

    @staticmethod
    def get_all_indexes(client: Elasticsearch) -> List[Index]:
        """
        Return all indexes in Elasticsearch and amount of documents.
        """
        indexes = client.cat.indices(h="index,docs.count", s="index").split()
        return [
            Index(name=name, docs_count=int(count))
            for name, count in chunkify(lst=indexes, n=2)
        ]

    @staticmethod
    def _get_reindex_body(es_index: str, source_es_host: str):
        """
        Return ElasticSearch reindex body for API request.
        """
        return {
            "source": {"remote": {"host": source_es_host}, "index": es_index},
            "conflicts": "proceed",
            "dest": {"index": es_index},
        }

    @staticmethod
    def _get_es_client(es_host: str) -> Elasticsearch:
        """
        Ping ElasticSearch server and return initialized client object.
        """
        client = Elasticsearch(hosts=es_host)
        try:
            client.ping()
        except ConnectionError:
            raise ElasticSearchNodeNotFoundException(
                message=ES_NODE_NOT_FOUND_ERROR.format(host=es_host)
            )
        else:
            return client
