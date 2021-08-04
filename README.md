Elasticsearch Reindex
====================

Local install
-------------

Setup and activate a python3 virtualenv via your preferred method. e.g. and install production requirements:

    $ make ve

To remove virtualenv:

    $ make clean

To install github hooks:

    $ make install_hooks

Tests
======================

Firstly add tests to `PYTHONPATH`

    $ export PYTHONPATH="."

For the rest testing with `pytest`

    $ pytest
