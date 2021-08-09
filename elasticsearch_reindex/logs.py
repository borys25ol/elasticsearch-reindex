import logging
from logging import Logger

from elasticsearch_reindex.const import LOG_FORMAT


def create_logger(logger_name: str) -> Logger:
    """
    Initialize logger for project.
    """
    logger = logging.getLogger(logger_name)

    logging.basicConfig(format=LOG_FORMAT)
    logger.setLevel(level=logging.INFO)

    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("elasticsearch").setLevel(logging.ERROR)

    return logger
