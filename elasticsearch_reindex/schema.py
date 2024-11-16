from dataclasses import dataclass

from elasticsearch_reindex.const import (
    DEFAULT_CHECK_INTERVAL,
    DEFAULT_CONCURRENT_TASKS,
    DEFAULT_REQUEST_TIMEOUT,
)


@dataclass
class Index:
    """
    Dataclass for storing ES index cat data.
    """

    name: str
    docs_count: int


@dataclass
class HttpAuth:
    """
    Dataclass for storing HTTP auth data.
    """

    username: str
    password: str

    def as_tuple(self) -> tuple[str, str]:
        return self.username, self.password


@dataclass
class Config:
    """
    Dataclass for storing init CLI args.
    """

    source_host: str
    dest_host: str
    source_http_auth: str | None
    dest_http_auth: str | None
    indexes: list[str] | None
    request_timeout: int = DEFAULT_REQUEST_TIMEOUT
    concurrent_tasks: int = DEFAULT_CONCURRENT_TASKS
    check_interval: int = DEFAULT_CHECK_INTERVAL

    @property
    def http_auth_dest(self) -> HttpAuth | None:
        if self.dest_http_auth:
            return _parse_auth_string(self.dest_http_auth)

    @property
    def http_auth_source(self) -> HttpAuth | None:
        if self.source_http_auth:
            return _parse_auth_string(self.source_http_auth)


def _parse_auth_string(auth_string: str) -> HttpAuth:
    """
    Parse destination HTTP auth string into HttpAuth object.

    :param auth_string: Destination HTTP auth string in format 'username:password'.
    :return: Parsed HttpAuth object.
    """
    auth_data = auth_string.split(":", 1)
    if len(auth_data) != 2:
        raise ValueError(
            "Invalid destination HTTP auth format. Expected 'username:password'"
        )
    return HttpAuth(username=auth_data[0], password=auth_data[1])
