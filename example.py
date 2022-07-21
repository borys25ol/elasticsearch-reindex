#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
    example.py
    ~~~~~~~~
    Support HTTP Basic authentication uses the basic_auth parameter
    by passing in a username and password within a tuple

    :author: Fufu, 2022/7/18
"""
from elasticsearch_reindex import Manager


def main() -> None:
    """
    Example reindex function with HTTP Basic authentication.
    """
    config = {
        "source_host": "http://localhost:9201",
        "dest_host": "http://localhost:9202",
        "check_interval": 20,
        "concurrent_tasks": 5,
        "indexes": ["es-index-1", "es-index-2", "es-index-n", "ff_220718"],
        # If the source host requires authentication
        # "source_http_auth": "tmp-source-user:tmp-source-PASSWD.220718",
        # If the destination host requires authentication
        "dest_http_auth": "tmp-reindex-user:tmp--PASSWD.220718",
    }
    manager = Manager.from_dict(data=config)
    manager.start_reindex()


if __name__ == "__main__":
    main()
