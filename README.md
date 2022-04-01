Elasticsearch Reindex
====================

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Pre-commit: enabled](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat)](https://github.com/pre-commit/pre-commit)

## Description
This tool can be used to transfer Elasticsearch indexes between different servers.

## Installing

```bash
pip install elasticsearch-reindex
```

How to use
-------------

Whitelist `source_host` Elasticsearch  in `dest_host` Elasticsearch.

You should edit Elasticsearch YML config:

#### Config path:

    $ /etc/elasticsearch/elasticsearch.yml

Add setting to the end of the file:

    $ reindex.remote.whitelist: <es-source-host>:<es-source-port>

Use CLI for run migration data:


    $ elasticsearch_reindex \
        --source_host http(s)://es-source-host:es-source-port \
        --dest_host http(s)://es-dest-host:es-dest-port \
        --check_interval 5 \
        --concurrent_tasks 3 \
        -i test_index_1 -i test_index_2 


### CLI Params description (example):

Required fields:

* `source_host` - Elasticsearch endpoint where data will be extracted.

* `dest_host` - Elasticsearch endpoint where data will be transfered.

Optional fields:

* `check_interval` - Time period (in second) to check task success status.

    `Default value` - `10` (seconds)

* `concurrent_tasks` - How many parallel task Elasticsearch will process.

    `Default value` - `1` (sync mode)

* `indexes` - List of user ES indexes to migrate instead of all source indexes.


### Run library from Python script:

```python
from elasticsearch_reindex import Manager


def main() -> None:
  """
  Example reindex function.
  """
  config = {
    "source_host": "http://localhost:9201",
    "dest_host": "http://localhost:9202",
    "check_interval": 20,
    "concurrent_tasks": 5,
  }
  manager = Manager.from_dict(data=config)
  manager.start_reindex()


if __name__ == "__main__":
  main()

```

With custom user indexes:
```python
from elasticsearch_reindex import Manager


def main() -> None:
  """
  Example reindex function.
  """
  config = {
    "source_host": "http://localhost:9201",
    "dest_host": "http://localhost:9202",
    "check_interval": 20,
    "concurrent_tasks": 5,
    "indexes": ["es-index-1", "es-index-2", "es-index-n"]
  }
  manager = Manager.from_dict(data=config)
  manager.start_reindex()


if __name__ == "__main__":
  main()

```

Local install
-------------

Setup and activate a python3 virtualenv via your preferred method. e.g. and install production requirements:

    $ make ve

To remove virtualenv:

    $ make clean

To install github hooks:

    $ make install_hooks

Create .env file and fill the data:

    $ cp .env.example .env

Export env variables:

    $ export $(xargs < .env)

### Env variables description:

Variable for enable testing:

* `ENV` - variable for enable testing mode.
For activate test mode set to value - `test`.

Elasticsearch docker settings:

* `ES_SOURCE_PORT` - Source Elasticsearch port


* `ES_DEST_PORT` - Destination Elasticsearch port


* `ES_VERSION` - Elasticsearch version


* `LOCAL_IP` - Address of you local host machine in LAN like `192.168.4.106`.

You can find it in:

* Mac OS:


    $ ifconfig

* Linux (find it in response):


    $ ip r

Tests
======================
Firstly up docker-compose services with 2 nodes of ElasticSearch:

    $ docker-compose up -d

Ensure that Elasticsearch nodes started correctly.

Env variables set from `.env` file.

For Source Elasticsearch:

    $ curl -X GET $LOCAL_IP:$ES_SOURCE_PORT


For destination Elasticsearch:

    $ curl -X GET $LOCAL_IP:$ES_DEST_PORT


Export to `PYTHONPATH` env variable:

    $ export PYTHONPATH="."

For run tests with `pytest` use:

    $ pytest ./tests
