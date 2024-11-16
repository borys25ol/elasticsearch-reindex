import os
from concurrent.futures import Future, ThreadPoolExecutor, as_completed

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
        self.config = config
        self.es_dest_client = ElasticsearchClient.from_config(
            config=config.dest_es_config
        )
        self.es_source_client = ElasticsearchClient.from_config(
            config=config.source_es_config
        )
        self.reindex_service = ReindexService(self.config)

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
        Branching logic by input action.
        """
        source_indexes = self.es_source_client.get_indexes()

        if user_indexes := self.config.indexes:
            source_indexes = self._filter_user_indexes(
                user_indexes=user_indexes, source_indexes=source_indexes
            )
        logger.info(f"Source elastic has {len(source_indexes)} indexes")

        dest_indexes = self.es_dest_client.get_indexes()
        logger.info(f"Destination elastic has {len(dest_indexes)} indexes")

        not_migrated_indexes, partial_migrated_indexes = check_migrated_indexes(
            source_indexes=source_indexes, dest_indexes=dest_indexes
        )
        logger.info(
            f"Not migrated es indexes: {len(not_migrated_indexes)}/{len(source_indexes)}"
        )
        logger.info(
            f"Partial migrated es indexes: {len(partial_migrated_indexes)}/{len(source_indexes)}"
        )

        # Calculate max concurrent task depends on CPU count.
        max_workers = min(self.config.concurrent_tasks, (os.cpu_count() or 1) * 5)
        executor = ThreadPoolExecutor(max_workers=max_workers)

        futures = {}
        for es_index in not_migrated_indexes:
            kwargs = {
                "es_index": es_index,
                "check_interval": self.config.check_interval,
            }
            future = executor.submit(self.reindex_service.transfer_index, **kwargs)
            futures[future] = es_index

        self._process_result(futures=futures)

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

    @staticmethod
    def _filter_user_indexes(
        user_indexes: list[str], source_indexes: list[Index]
    ) -> list[Index]:
        """
        Filter source indexes by user provided indexes.
        """
        return [index for index in source_indexes if index.name in user_indexes]
