"""
Module configuration custom logger.
"""

import logging
from functools import lru_cache
from typing import Any

DEFAULT_LOGGER_NAME = "elasticsearch-reindex"

LOG_MESSAGE_FORMAT = "[%(name)s] [%(asctime)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%dT%T"


class CustomHandler(logging.StreamHandler):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        formatter = logging.Formatter(fmt=LOG_MESSAGE_FORMAT, datefmt=LOG_DATE_FORMAT)
        self.setFormatter(fmt=formatter)


def _get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name=name)

    logger.setLevel(level=level)
    logger.addHandler(hdlr=CustomHandler())

    return logger


@lru_cache(maxsize=None)
def create_logger(name: str = DEFAULT_LOGGER_NAME) -> logging.Logger:
    """
    Initialize logger for project.
    """
    return _get_logger(name)
