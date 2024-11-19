"""
Module with project constants.
"""

# Endpoint for create internal ElasticSearch reindex task.
ES_CREATE_REINDEX_TASK_ENDPOINT = "{es_host}/_reindex?pretty&wait_for_completion=false"
ES_CHECK_REINDEX_TASK_ENDPOINT = "{es_host}/_tasks/{task_id}"

DEFAULT_CHECK_INTERVAL = 10
DEFAULT_CONCURRENT_TASKS = 1
DEFAULT_REQUEST_TIMEOUT = 60
