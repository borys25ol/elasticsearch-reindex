from time import sleep

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
from elasticsearch_reindex.schema import Config, HttpAuth

logger = create_logger(__name__)


class ReindexService:
    """
    This class provide simple interface to ElasticSearch reindex API.
    """

    def __init__(self, config: Config):
        self.config = config
        self._es_service = ElasticsearchClient(config)

    def transfer_index(self, es_index: str, check_interval: int = 10) -> str:
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
                dest_es_host=self.config.dest_host,
                task_id=task_id,
                http_auth=self.config.http_auth_dest,
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

        auth = (
            self.config.http_auth_dest.as_tuple()
            if self.config.http_auth_dest
            else None
        )
        response = requests.post(
            url=endpoint,
            json=reindex_payload,
            headers=HEADERS,
            auth=auth,
            timeout=self.config.request_timeout,
        )
        return response.json()["task"]

    @staticmethod
    def _check_task_completed(
        dest_es_host: str, task_id: str, http_auth: HttpAuth | None
    ) -> tuple[bool, dict[str, int]]:
        """
        Make request to Elasticsearch Tasks API and check task status.
        """
        endpoint = ES_CHECK_TASK_ENDPOINT.format(es_host=dest_es_host, task_id=task_id)

        auth = http_auth.as_tuple() if http_auth else None
        response = requests.get(url=endpoint, auth=auth, timeout=60).json()

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

    def _get_reindex_body(self, es_index: str) -> dict:
        """
        Return ElasticSearch reindex body for API request.
        """
        remote_settings = {"host": self.config.source_host}
        if self.config.http_auth_source:
            remote_settings = remote_settings | {
                "username": self.config.http_auth_source.username,
                "password": self.config.http_auth_source.password,
            }

        body = {
            "source": {"remote": remote_settings, "index": es_index},
            "conflicts": "proceed",
            "dest": {"index": es_index},
        }
        return body
