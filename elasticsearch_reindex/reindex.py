from dataclasses import dataclass
from time import sleep
from typing import Dict, List, Tuple

import requests
from elasticsearch import exceptions
from elasticsearch.client import Elasticsearch

from elasticsearch_reindex.const import (
    DEFAULT_ES_KWARGS,
    ES_CHECK_TASK_ENDPOINT,
    ES_CREATE_TASK_ENDPOINT,
    HEADERS,
    LOCAL_SOURCE_HOST,
    TEST_ENV,
)
from elasticsearch_reindex.errors import (
    ES_NODE_NOT_FOUND_ERROR,
    ES_TASK_ID_ERROR,
    ElasticSearchInvalidTaskIDException,
    ElasticSearchNodeNotFoundException,
)
from elasticsearch_reindex.logs import create_logger
from elasticsearch_reindex.utils import chunkify

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

    def get_user_indexes(self, indexes: List[str]) -> List[Index]:
        """
        Compare indexes provided by user.
        Return indexes for migration.

        :param indexes: List of user indexes.
        :return: List of `Index` objects.
        """
        source_indexes = self.get_all_indexes(client=self.source_client)
        return [index for index in source_indexes if index.name in set(indexes)]

    def check_migrated_indexes(
        self, source_indexes: List[Index], dest_indexes: List[Index]
    ) -> Tuple[list, list]:
        """
        Check if index from `source_indexes` exist in `dest_indexes`.
        If index already exist we should check if all documents was transferred.
        """
        source_indexes = self._get_flatten_dict(data=source_indexes)
        dest_indexes = self._get_flatten_dict(data=dest_indexes)

        not_migrated, partial_migrated = [], []

        for index in source_indexes:
            if index in dest_indexes:
                if source_indexes[index] != dest_indexes[index]:
                    partial_migrated.append(index)
            else:
                not_migrated.append(index)

        return not_migrated, partial_migrated

    def transfer_index(
        self,
        es_index: str,
        source_es_host: str,
        dest_es_host: str,
        check_interval: int = 10,
    ) -> str:
        """
        Create reindex task and waiting for finish this task.

        :param es_index: Elasticsearch index.
        :param source_es_host: Source Elasticsearch host.
        :param dest_es_host: Destination Elasticsearch host.
        :param check_interval: Period of request task status (in seconds).
        """
        task_id = self._create_reindex_task(
            es_index=es_index,
            source_es_host=source_es_host,
            dest_es_host=dest_es_host,
        )
        logger.info(f"Got task for migrate data: {task_id}")

        # Wait for Elasticsearch manage input task.
        sleep(2)

        while True:
            completed, status = self._check_task_completed(
                dest_es_host=self.dest_es_host, task_id=task_id
            )
            logger.info(
                f"Task id: {task_id}. "
                f"Migrated documents: {status['created']}/{status['total']}"
            )
            if not completed:
                sleep(check_interval)
                continue

            logger.info(f"Task finished: {task_id}")
            break

        return task_id

    def _create_reindex_task(
        self, es_index: str, source_es_host: str, dest_es_host: str
    ) -> str:
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
    def _check_task_completed(
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
        source_host = LOCAL_SOURCE_HOST if TEST_ENV else source_es_host
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
        client = Elasticsearch(hosts=es_host, **DEFAULT_ES_KWARGS)
        try:
            client.info()
        except exceptions.ConnectionError:
            raise ElasticSearchNodeNotFoundException(
                message=ES_NODE_NOT_FOUND_ERROR.format(host=es_host)
            )
        else:
            return client

    @staticmethod
    def _get_flatten_dict(data: List[Index]) -> dict:
        """
        Convert list of dataclasses to dict for fast searching.
        """
        return {index.name: index.docs_count for index in data}
