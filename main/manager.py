from argparse import Namespace
from time import sleep

from main.logs import create_logger
from main.reindex import ReindexService

logger = create_logger(__name__)


class Manager:
    """
    Logic for input args handling.
    """

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def start_reindex(self) -> None:
        """
        Branching logic by input action.
        """
        source_es_host, dest_es_host = self.args.source_host, self.args.dest_host

        reindex_service = ReindexService(source_es_host, dest_es_host)

        source_indexes = reindex_service.get_all_indexes(
            client=reindex_service.source_client
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

        for es_index in list(not_migrated)[:1]:
            task_id = reindex_service.transfer_index(
                es_index=es_index,
                source_es_host=source_es_host,
                dest_es_host=dest_es_host,
            )
            logger.info(f"Got task for migrate data: {task_id}")

            # Wait for Elasticsearch manage input task.
            sleep(2)

            while True:
                completed, status = reindex_service.check_task_completed(
                    dest_es_host=self.args.dest_host, task_id=task_id
                )
                logger.info(
                    f"Task id: {task_id}. "
                    f"Migrated documents: {status['created']}/{status['total']}"
                )
                if not completed:
                    sleep(10)
                    continue

                logger.info(f"Task finished: {task_id}\n")
                break
