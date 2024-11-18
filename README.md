Elasticsearch Reindex
====================

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Pre-commit: enabled](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat)](https://github.com/pre-commit/pre-commit)

## Description
`elasticsearch-reindex` is a CLI tool for transferring Elasticsearch indexes between different servers.

## Installing

Install the package using pip:

```bash
pip install elasticsearch-reindex
```

Usage
-----

## Configuration

Ensure the source Elasticsearch host is whitelisted in the destination host.
Edit the elasticsearch.yml configuration file on the destination Elasticsearch server.

You should edit Elasticsearch YML config:

#### Path to config file:

```shell
/etc/elasticsearch/elasticsearch.yml
```

Add the following line to the file:

```shell
reindex.remote.whitelist: <es-source-host>:<es-source-port>
```


## Running the Tool

Use the CLI to migrate data between Elasticsearch instances:
```shell
elasticsearch_reindex \
        --source_host http(s)://es-source-host:es-source-port \
        --source_http_auth username:password \
        --dest_host http(s)://es-dest-host:es-dest-port \
        --dest_http_auth username:password \
        --check_interval 5 \
        --concurrent_tasks 3 \
        -i test_index_1 -i test_index_2
```

Also, there is a command alias `elasticsearch-reindex`:
```shell
elasticsearch-reindex ...
```

### CLI Parameters


Required fields:

* `source_host` - Elasticsearch endpoint where data will be extracted.

* `dest_host` - Elasticsearch endpoint where data will be transfered.

Optional fields:

* `source_http_auth` - HTTP Basic authentication, username and password.

* `dest_http_auth` - HTTP Basic authentication, username and password.

* `check_interval` - Time period (in second) to check task success status.

    `Default value` - `10` (seconds)

* `concurrent_tasks` - How many parallel task Elasticsearch will process.

    `Default value` - `1` (sync mode)

* `indexes` - List of user ES indexes to migrate instead of all source indexes.


### Run library from Python script:

```python
from elasticsearch_reindex import ReindexManager


def main() -> None:
  """
  Example reindex function.
  """
  dict_config = {
    "source_host": "http://localhost:9201",
    "dest_host": "http://localhost:9202",
    "check_interval": 20,
    "concurrent_tasks": 5,
  }
  reindex_manager = ReindexManager.from_dict(data=dict_config)
  reindex_manager.start_reindex()


if __name__ == "__main__":
  main()

```

With custom user indexes:

```python
from elasticsearch_reindex import ReindexManager


def main() -> None:
  """
  Example reindex function with HTTP Basic authentication.
  """
  dict_config = {
    "source_host": "http://localhost:9201",
    # If the source host requires authentication
    # "source_http_auth": "tmp-source-user:tmp-source-PASSWD.220718",
    "dest_host": "http://localhost:9202",
    # If the destination host requires authentication
    # "dest_http_auth": "tmp-reindex-user:tmp--PASSWD.220718",
    "check_interval": 20,
    "concurrent_tasks": 5,
    "indexes": ["es-index-1", "es-index-2", "es-index-n"],
  }
  reindex_manager = ReindexManager.from_dict(data=dict_config)
  reindex_manager.start_reindex()


if __name__ == "__main__":
  main()

```

Local install
-------------

Set up and activate a Python 3 virtual environment:

```shell
make ve
```

To install Git hooks:

```shell
make install_hooks
```

Create .env file and fill the data:
```shell
cp .env.example .env
```

Export env variables:
```shell
export $(xargs < .env)
```

### Key Environment Variables::

Variable for enable testing:

* `ENV` - variable for enable testing mode.
For activate test mode set to value - `test`.

Elasticsearch docker settings:

* `ES_SOURCE_PORT` - Source Elasticsearch port

* `ES_DEST_PORT` - Destination Elasticsearch port

* `ES_VERSION` - Elasticsearch version

* `LOCAL_IP` - Address of you local host machine in LAN like `192.168.4.106`.

### How to find your Local IP?

* MacOS (find it in response):
```shell
ifconfig
```

* Linux (find it in response):
```shell
ip r
```

Testing
-------

Start Elasticsearch nodes using Docker Compose:
```shell
docker-compose up -d
```

Verify Elasticsearch nodes are running:

* Source Elasticsearch:

```shell
curl -X GET $LOCAL_IP:$ES_SOURCE_PORT
```

* Destination Elasticsearch:

```shell
curl -X GET $LOCAL_IP:$ES_DEST_PORT
```


Export to `PYTHONPATH` env variable:
```shell
export PYTHONPATH="."
```

For run tests with `pytest` use:
```shell
make test
```

For run tests with `pytest` and `coverage` report use:
```shell
make test-cov
```
