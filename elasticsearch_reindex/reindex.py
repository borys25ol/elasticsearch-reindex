from time import sleep

import requests

from elasticsearch_reindex.const import (
    ES_CHECK_REINDEX_TASK_ENDPOINT,
    ES_CREATE_REINDEX_TASK_ENDPOINT,
)
from elasticsearch_reindex.errors import (
    ES_TASK_ID_ERROR,
    ElasticSearchInvalidTaskIDException,
)
from elasticsearch_reindex.logger import create_logger
from elasticsearch_reindex.schema import Config

logger = create_logger()


class ReindexService:
    """
    This class provide simple interface to ElasticSearch Reindex API.
    """

    # Default Headers for call ElasticSearch API.
    headers = {"Content-Type": "application/json"}

    # Sleep interval before start checking ElasticSearch tasks statuses.
    initial_sleep_interval = 2

    def __init__(self, config: Config):
        self.config = config

    @property
    def http_auth(self) -> tuple[str, str] | None:
        """
        Return HTTP auth credentials if provided.
        """
        return (
            self.config.http_auth_dest.as_tuple()
            if self.config.http_auth_dest
            else None
        )

    def transfer_index(self, es_index: str, check_interval: int = 10) -> str:
        """
        Create reindex task and wait for it to finish.

        Args:
            es_index (str): Elasticsearch index to reindex.
            check_interval (int): Interval between task status checks in seconds. Defaults to 10.

        Returns:
            str: The ID of the completed reindex task.
        """
        task_id = self._create_reindex_task(es_index=es_index)
        logger.info(f"Reindex task: {task_id}")

        # Wait for Elasticsearch manage input task.
        sleep(self.initial_sleep_interval)

        return self._wait_for_task_completion(
            task_id=task_id, check_interval=check_interval
        )

    def _create_reindex_task(self, es_index: str) -> str:
        """
        Create reindex task via Elasticsearch API.
        """
        response = requests.post(
            url=ES_CREATE_REINDEX_TASK_ENDPOINT.format(es_host=self.config.dest_host),
            json=self._get_reindex_body(es_index=es_index),
            headers=self.headers,
            auth=self.http_auth,
            timeout=self.config.request_timeout,
        )
        return response.json()["task"]

    def _check_task_completed(self, task_id: str) -> tuple[bool, dict[str, int]]:
        """
        Make request to Elasticsearch Tasks API and check task status.
        """
        endpoint = ES_CHECK_REINDEX_TASK_ENDPOINT.format(
            es_host=self.config.dest_host, task_id=task_id
        )
        response = requests.get(url=endpoint, auth=self.http_auth, timeout=60)

        json_data = response.json()

        if err_data := json_data.get("error"):
            self._handle_error(err_data=err_data, task_id=task_id)

        response_status = json_data["task"]["status"]

        return json_data["completed"], {
            "total": response_status["total"],
            "created": response_status["created"],
        }

    def _get_reindex_body(self, es_index: str) -> dict:
        """
        Return ElasticSearch reindex body for API request.

        This method creates a dictionary that represents the body of a reindex API request
        to ElasticSearch.
        """
        remote_settings = self._get_remote_settings()
        return {
            "source": {"remote": remote_settings, "index": es_index},
            "conflicts": "proceed",
            "dest": {"index": es_index},
        }

    def _get_remote_settings(self) -> dict[str, str]:
        """
        Return remote settings with authentication if provided.
        """
        remote_settings = {"host": self.config.source_host}

        if self.config.http_auth_source:
            remote_settings.update(
                {
                    "username": self.config.http_auth_source.username,
                    "password": self.config.http_auth_source.password,
                }
            )

        return remote_settings

    def _handle_error(self, err_data: dict, task_id: str) -> None:
        """
        Handle errors in the Elasticsearch response.

        Args:
            err_data (Dict): The JSON error response from Elasticsearch.
            task_id (str): The ID of the task being checked.

        Raises:
            ElasticSearchInvalidTaskIDException: If the task ID is invalid.
        """
        logger.error(f"Error during task check: {err_data}")

        if err_data["type"] == "illegal_argument_exception":
            raise ElasticSearchInvalidTaskIDException(
                ES_TASK_ID_ERROR.format(host=self.config.dest_host, task_id=task_id)
            )

    def _wait_for_task_completion(self, task_id: str, check_interval: int) -> str:
        """
        Wait for the reindex task to complete, periodically checking its status.

        Args:
            task_id (str): The ID of the reindex task.
            check_interval (int): Interval between status checks in seconds.

        Returns:
            str: The ID of the completed task.

        Raises:
            ElasticSearchInvalidTaskIDException: If the task ID becomes invalid during execution.
        """
        while True:
            completed, info = self._check_task_completed(task_id=task_id)
            self._log_migration_progress(task_id=task_id, info=info)

            if completed:
                logger.info(f"Task finished: {task_id}")
                return task_id

            sleep(check_interval)

    @staticmethod
    def _log_migration_progress(task_id: str, info: dict[str, int]) -> None:
        """
        Log the progress of the migration task.

        Args:
            task_id (str): The ID of the reindex task.
            info (Dict[str, int]): Dictionary containing 'created' and 'total' document counts.
        """
        created, total = info["created"], info["total"]
        logger.info(f"Migrated {created}/{total} documents for task {task_id}")
