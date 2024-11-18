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
class ElasticsearchConfig:
    """
    Dataclass for storing Elasticsearch configuration data.
    """

    host: str
    http_auth: HttpAuth | None


def parse_auth_string(auth_string: str) -> HttpAuth:
    """
    Parse a HTTP authentication string into a HttpAuth object.

    This function takes a string containing username and password separated by a colon,
    splits it, and creates a HttpAuth object with the parsed values.

    Args:
        auth_string (str): A string containing HTTP authentication credentials
                           in the format 'username:password'.

    Returns:
        HttpAuth: An object containing the parsed username and password.

    Raises:
        ValueError: If the auth_string is not in the correct format.

    Example:
        auth = _parse_auth_string("user:pass123")
        print(auth.username, auth.password)
        user pass123
    """
    auth_data = auth_string.split(":", 1)
    if len(auth_data) != 2:
        raise ValueError(
            "Invalid destination HTTP auth format. Expected 'username:password'"
        )
    return HttpAuth(username=auth_data[0], password=auth_data[1])


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
            return parse_auth_string(self.dest_http_auth)

    @property
    def http_auth_source(self) -> HttpAuth | None:
        if self.source_http_auth:
            return parse_auth_string(self.source_http_auth)

    @property
    def dest_es_config(self) -> ElasticsearchConfig:
        return ElasticsearchConfig(host=self.dest_host, http_auth=self.http_auth_dest)

    @property
    def source_es_config(self) -> ElasticsearchConfig:
        return ElasticsearchConfig(
            host=self.source_host, http_auth=self.http_auth_source
        )
