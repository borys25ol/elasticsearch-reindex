from dataclasses import dataclass
from typing import List, Optional

from elasticsearch_reindex.const import DEFAULT_CHECK_INTERVAL, DEFAULT_CONCURRENT_TASKS


@dataclass
class Index:
    """
    Dataclass for storing ES index cat data.
    """

    name: str
    docs_count: int


@dataclass
class Config:
    """
    Dataclass for storing init CLI args.
    """

    source_host: str
    dest_host: str
    indexes: Optional[List[str]]
    concurrent_tasks: int = DEFAULT_CONCURRENT_TASKS
    check_interval: int = DEFAULT_CHECK_INTERVAL
