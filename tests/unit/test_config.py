import pytest

from elasticsearch_reindex.const import (
    DEFAULT_CHECK_INTERVAL,
    DEFAULT_CONCURRENT_TASKS,
    DEFAULT_REQUEST_TIMEOUT,
)
from elasticsearch_reindex.schema import (
    Config,
    ElasticsearchConfig,
    HttpAuth,
    parse_auth_string,
)


def test_http_auth_as_tuple():
    auth = HttpAuth(username="user", password="pass123")
    assert auth.as_tuple() == ("user", "pass123")


def test_parse_auth_string_valid():
    auth = parse_auth_string("user:pass123")
    assert auth.username == "user"
    assert auth.password == "pass123"


def test_parse_auth_string_invalid():
    with pytest.raises(ValueError, match="Invalid destination HTTP auth format"):
        parse_auth_string("invalid_format")


def test_config_http_auth_properties():
    config = Config(
        source_host="http://source.example.com",
        dest_host="http://dest.example.com",
        source_http_auth="user1:pass1",
        dest_http_auth="user2:pass2",
        indexes=None,
    )
    assert config.http_auth_source.username == "user1"
    assert config.http_auth_source.password == "pass1"
    assert config.http_auth_dest.username == "user2"
    assert config.http_auth_dest.password == "pass2"


def test_config_http_without_auth_properties():
    config = Config(
        source_host="http://source.example.com",
        dest_host="http://dest.example.com",
        source_http_auth=None,
        dest_http_auth=None,
        indexes=None,
    )
    assert config.http_auth_source is None
    assert config.http_auth_source is None


def test_config_es_config_properties():
    config = Config(
        source_host="http://source.example.com",
        dest_host="http://dest.example.com",
        source_http_auth="user1:pass1",
        dest_http_auth="user2:pass2",
        indexes=None,
    )
    source_es_config = config.source_es_config
    dest_es_config = config.dest_es_config

    assert isinstance(source_es_config, ElasticsearchConfig)
    assert source_es_config.host == "http://source.example.com"
    assert source_es_config.http_auth.username == "user1"
    assert source_es_config.http_auth.password == "pass1"

    assert isinstance(dest_es_config, ElasticsearchConfig)
    assert dest_es_config.host == "http://dest.example.com"
    assert dest_es_config.http_auth.username == "user2"
    assert dest_es_config.http_auth.password == "pass2"


def test_config_defaults():
    config = Config(
        source_host="http://source.example.com",
        dest_host="http://dest.example.com",
        source_http_auth=None,
        dest_http_auth=None,
        indexes=["index1"],
    )
    assert config.request_timeout == DEFAULT_REQUEST_TIMEOUT
    assert config.concurrent_tasks == DEFAULT_CONCURRENT_TASKS
    assert config.check_interval == DEFAULT_CHECK_INTERVAL
