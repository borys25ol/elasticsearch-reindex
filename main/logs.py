import logging
from logging import Logger

from main import const


def create_logger(logger_name: str) -> Logger:
    """
    Initialize logger for project.
    """
    logger = logging.getLogger(logger_name)

    logging.basicConfig(format=const.LOG_FORMAT)
    logger.setLevel(level=logging.INFO)

    return logger
