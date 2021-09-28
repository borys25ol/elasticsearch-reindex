import os
from argparse import Namespace
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from elasticsearch_reindex import const
from elasticsearch_reindex.logs import create_logger
from elasticsearch_reindex.reindex import ReindexService

logger = create_logger(__name__)


@dataclass
class Config:
    """
    Dataclass for storing init CLI args.
    """

    source_host: str
    dest_host: str
    check_interval: Optional[int]
    concurrent_tasks: Optional[int]
    indexes: Optional[List[str]]


class Manager:
    """
    Logic for input args handling.
    """

    def __init__(self, args: Union[Namespace, Config]) -> None:
        self.args = args

    @classmethod
    def from_dict(cls, data: dict):
        """
        Initialize Manages class from dict settings.
        """
        config = Config(
            source_host=data["source_host"],
            dest_host=data["dest_host"],
            check_interval=data.get("check_interval"),
            concurrent_tasks=data.get("concurrent_tasks"),
            indexes=data.get("indexes", []),
        )
        return cls(args=config)

    def start_reindex(self) -> None:
        """
        Branching logic by input action.
        """
        source_host, dest_host = self.args.source_host, self.args.dest_host
        check_interval = self.args.check_interval or const.DEFAULT_CHECK_INTERVAL
        concurrent_tasks = self.args.concurrent_tasks or const.DEFAULT_CONCURRENT_TASKS
        user_indexes = self.args.indexes

        reindex_service = ReindexService(
            source_es_host=source_host, dest_es_host=dest_host
        )
        if user_indexes:
            source_indexes = reindex_service.get_user_indexes(indexes=user_indexes)
        else:
            source_indexes = reindex_service.get_all_indexes(
                client=reindex_service.source_client,
            )
        logger.info(f"Source ES host has {len(source_indexes)} indexes")

        dest_indexes = reindex_service.get_all_indexes(
            client=reindex_service.dest_client
        )
        logger.info(f"Destination ES host has {len(dest_indexes)} indexes\n")

        not_migrated, partial_migrated = reindex_service.check_migrated_indexes(
            source_indexes=source_indexes, dest_indexes=dest_indexes
        )
        logger.info(
            f"Not migrated ES indexes: {len(not_migrated)}/{len(source_indexes)}"
        )
        logger.info(
            f"Partial migrated ES indexes: {len(partial_migrated)}/{len(source_indexes)}\n"
        )

        # Calculate max concurrent task depends on CPU count.
        max_workers = min(concurrent_tasks, (os.cpu_count() or 1) * 5)
        executor = ThreadPoolExecutor(max_workers=max_workers)

        futures = {}
        for es_index in not_migrated:
            kwargs = {
                "es_index": es_index,
                "source_es_host": source_host,
                "dest_es_host": dest_host,
                "check_interval": check_interval,
            }
            future = executor.submit(reindex_service.transfer_index, **kwargs)
            futures[future] = es_index

        self._process_result(futures=futures)

    @staticmethod
    def _process_result(futures: Dict[Future, str]) -> None:
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
