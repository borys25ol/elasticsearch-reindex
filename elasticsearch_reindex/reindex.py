from time import sleep
from typing import Dict, Optional, Tuple, Union

import requests

from elasticsearch_reindex.client import ElasticsearchClient
from elasticsearch_reindex.const import (
    ES_CHECK_TASK_ENDPOINT,
    ES_CREATE_TASK_ENDPOINT,
    HEADERS,
)
from elasticsearch_reindex.errors import (
    ES_TASK_ID_ERROR,
    ElasticSearchInvalidTaskIDException,
)
from elasticsearch_reindex.logs import create_logger
from elasticsearch_reindex.schema import Config

logger = create_logger(__name__)


class ReindexService:
    """
    This class provide simple interface to ElasticSearch reindex API.
    """

    def __init__(self, config: Config):
        self.config = config
        self._es_service = ElasticsearchClient(config)

    def transfer_index(
        self,
        es_index: str,
        check_interval: int = 10,
    ) -> str:
        """
        Create reindex task and waiting for finish this task.

        :param es_index: Elasticsearch index.
        :param check_interval: Period of request task status (in seconds).
        """
        task_id = self._create_reindex_task(es_index=es_index)
        logger.info(f"Got task for migrate data: {task_id}")

        # Wait for Elasticsearch manage input task.
        sleep(2)

        while True:
            completed, status = self._check_task_completed(
                dest_es_host=self.config.dest_host, task_id=task_id, dest_http_auth=self.config.dest_http_auth
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

    def _create_reindex_task(self, es_index: str) -> str:
        """
        Create reindex task via Elasticsearch API.
        """
        endpoint = ES_CREATE_TASK_ENDPOINT.format(es_host=self.config.dest_host)
        reindex_payload = self._get_reindex_body(es_index=es_index)
        response = requests.post(url=endpoint, json=reindex_payload, headers=HEADERS, auth=self.config.dest_http_auth)
        task_id = response.json()["task"]
        return task_id

    @staticmethod
    def _check_task_completed(
        dest_es_host: str, task_id: str, dest_http_auth: Optional[Tuple[str]] = None
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Make request to Elasticsearch Tasks API and check task status.
        """
        endpoint = ES_CHECK_TASK_ENDPOINT.format(es_host=dest_es_host, task_id=task_id)
        response = requests.get(url=endpoint, auth=dest_http_auth).json()

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

    def _get_reindex_body(self, es_index: str) -> Dict[str, Union[str, dict]]:
        """
        Return ElasticSearch reindex body for API request.
        """
        body = {
            "source": {"remote": {"host": self.config.source_host}, "index": es_index},
            "conflicts": "proceed",
            "dest": {"index": es_index},
        }
        if self.config.source_http_auth:
            body["source"]["remote"]["username"], body["source"]["remote"]["password"] = self.config.source_http_auth
        return body
