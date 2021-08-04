from dataclasses import dataclass
from typing import Dict, List, Tuple

import requests
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError

from main.const import (
    ES_CHECK_TASK_ENDPOINT,
    ES_CREATE_TASK_ENDPOINT,
    ES_SOURCE_HOST,
    ES_SOURCE_PORT,
    HEADERS,
    TEST_ENV,
)
from main.errors import (
    ES_NODE_NOT_FOUND_ERROR,
    ES_TASK_ID_ERROR,
    ElasticSearchInvalidTaskIDException,
    ElasticSearchNodeNotFoundException,
)
from main.logs import create_logger
from main.utils import chunkify

logger = create_logger(__name__)


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
            if not name.startswith(".")
        ]

    @staticmethod
    def check_migrated_indexes(
        source_indexes: List[Index], dest_indexes: List[Index]
    ) -> Tuple[set, set]:
        """
        Check if index from `source_indexes` exist in `dest_indexes`.
        If index already exist we should check if all documents was transferred.
        """
        not_migrated = set()
        partial_migrated = set()

        flatten_source_indexes = {
            index.name: index.docs_count for index in source_indexes
        }
        flatten_dest_indexes = {index.name: index.docs_count for index in dest_indexes}

        for index in flatten_source_indexes:
            if index in flatten_dest_indexes:
                if flatten_source_indexes[index] != flatten_dest_indexes[index]:
                    partial_migrated.add(index)
            else:
                not_migrated.add(index)

        return not_migrated, partial_migrated

    def transfer_index(self, es_index: str, source_es_host: str, dest_es_host: str):
        """
        Create reindex task via Elasticsearch API.
        """
        endpoint = ES_CREATE_TASK_ENDPOINT.format(es_host=dest_es_host)

        reindex_payload = self._get_reindex_body(
            es_index=es_index, source_es_host=source_es_host
        )
        response = requests.post(url=endpoint, json=reindex_payload, headers=HEADERS)

        task_id = response.json()["task"]

        return task_id

    @staticmethod
    def check_task_completed(
        dest_es_host: str, task_id: str
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Make request to Elasticsearch Tasks API and check task status.
        """
        endpoint = ES_CHECK_TASK_ENDPOINT.format(es_host=dest_es_host, task_id=task_id)

        response = requests.get(url=endpoint).json()

        if (
            "error" in response
            and response["error"]["type"] == "illegal_argument_exception"
        ):
            raise ElasticSearchInvalidTaskIDException(
                message=ES_TASK_ID_ERROR.format(host=dest_es_host, task_id=task_id)
            )

        response_status = response["task"]["status"]

        data = {
            "total": response_status["total"],
            "created": response_status["created"],
        }

        return response["completed"], data

    @staticmethod
    def _get_reindex_body(es_index: str, source_es_host: str) -> Dict[str, str]:
        """
        Return ElasticSearch reindex body for API request.
        """
        source_host = (
            f"{ES_SOURCE_HOST}:{ES_SOURCE_PORT}" if TEST_ENV else source_es_host
        )
        return {
            "source": {"remote": {"host": source_host}, "index": es_index},
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
