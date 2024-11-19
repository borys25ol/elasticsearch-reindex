import os
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any

from elasticsearch_reindex.client import ElasticsearchClient
from elasticsearch_reindex.const import DEFAULT_CHECK_INTERVAL, DEFAULT_CONCURRENT_TASKS
from elasticsearch_reindex.logger import create_logger
from elasticsearch_reindex.reindex import ReindexService
from elasticsearch_reindex.schema import Config, Index
from elasticsearch_reindex.utils import check_migrated_indexes

logger = create_logger()


class ReindexManager:
    """
    Logic for input args handling.
    """

    def __init__(self, config: Config) -> None:
        self._config = config
        self._es_dest_client = ElasticsearchClient.from_config(
            config=config.dest_es_config
        )
        self._es_source_client = ElasticsearchClient.from_config(
            config=config.source_es_config
        )
        self._reindex_service = ReindexService(config=config)

    @classmethod
    def from_dict(cls, data: dict) -> "ReindexManager":
        """
        Initialize Manages class from dict settings.
        """
        config = Config(
            source_host=data["source_host"],
            dest_host=data["dest_host"],
            source_http_auth=data.get("source_http_auth"),
            dest_http_auth=data.get("dest_http_auth"),
            indexes=data.get("indexes", []),
            check_interval=data.get("check_interval", DEFAULT_CHECK_INTERVAL),
            concurrent_tasks=data.get("concurrent_tasks", DEFAULT_CONCURRENT_TASKS),
        )
        return cls(config=config)

    def start_reindex(self) -> None:
        """
        Start the reindexing process for Elasticsearch indexes.

        This method performs the following steps:
            1. Retrieves source and destination indexes
            2. Filters indexes based on user input (if provided)
            3. Identifies indexes that need migration
            4. Initiates concurrent reindexing tasks
            5. Processes the results of the reindexing tasks

        Raises:
            ElasticsearchException: If there's an error communicating with Elasticsearch
            Exception: For any other unexpected errors during the process
        """
        source_indexes = self._get_source_indexes()
        dest_indexes = self._get_destination_indexes()

        not_migrated_indexes, partial_migrated_indexes = self._identify_migration_needs(
            source_indexes=source_indexes, dest_indexes=dest_indexes
        )

        self._log_migration_status(
            source_indexes, dest_indexes, not_migrated_indexes, partial_migrated_indexes
        )
        if not not_migrated_indexes:
            logger.info("No indexes require migration. Process complete.")
            return

        try:
            self._execute_reindex_tasks(not_migrated_indexes)
        except Exception as e:
            logger.error(f"An error occurred during reindexing: {str(e)}")
            raise

    def _execute_reindex_tasks(self, not_migrated_indexes: list[str]) -> None:
        """
        Execute reindexing tasks concurrently.
        """
        # Calculate max concurrent task depends on CPU count.
        max_workers = min(self._config.concurrent_tasks, (os.cpu_count() or 1) * 5)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for es_index in not_migrated_indexes:
                kwargs: dict[str, Any] = {
                    "es_index": es_index,
                    "check_interval": self._config.check_interval,
                }
                future = executor.submit(self._reindex_service.transfer_index, **kwargs)
                futures[future] = es_index

            self._process_result(futures=futures)

    def _get_source_indexes(self) -> list[Index]:
        """
        Retrieve and filter source indexes.
        """
        source_indexes = self._es_source_client.get_indexes()
        if user_indexes := self._config.indexes:
            return self._filter_user_indexes(
                user_indexes=user_indexes, source_indexes=source_indexes
            )
        return source_indexes

    def _get_destination_indexes(self) -> list[Index]:
        """
        Retrieve destination indexes.
        """
        return self._es_dest_client.get_indexes()

    @staticmethod
    def _log_migration_status(
        source_indexes: list[Index],
        dest_indexes: list[Index],
        not_migrated_indexes: list[str],
        partial_migrated_indexes: list[str],
    ) -> None:
        """
        Log the status of indexes to be migrated.
        """
        logger.info(f"Source Elasticsearch contains {len(source_indexes)} indexes")
        logger.info(f"Destination Elasticsearch contains {len(dest_indexes)} indexes")
        logger.info(
            f"Indexes requiring full migration: "
            f"{len(not_migrated_indexes)}/{len(source_indexes)}"
        )
        logger.info(
            f"Indexes requiring partial migration: "
            f"{len(partial_migrated_indexes)}/{len(source_indexes)} "
        )

    @staticmethod
    def _identify_migration_needs(
        source_indexes: list[Index], dest_indexes: list[Index]
    ) -> tuple[list[str], list[str]]:
        """
        Identify indexes that need migration.
        """
        return check_migrated_indexes(
            source_indexes=source_indexes, dest_indexes=dest_indexes
        )

    @staticmethod
    def _filter_user_indexes(
        user_indexes: list[str], source_indexes: list[Index]
    ) -> list[Index]:
        """
        Filter source indexes by user provided indexes.
        """
        return [index for index in source_indexes if index.name in user_indexes]

    @staticmethod
    def _process_result(futures: dict[Future, str]) -> None:
        """
        Process ThreadPoolExecutor tasks result.
        """
        for future in as_completed(futures):
            index = futures[future]
            try:
                task_id = future.result()
                futures.pop(future, None)
            except Exception as exc:
                logger.error(f"Index: {index} generated an exception: {exc}")
            else:
                logger.info(f"Task id: {task_id}. Reindex completed: {index}.")
                logger.info(f"Tasks left: {len(futures)}")
