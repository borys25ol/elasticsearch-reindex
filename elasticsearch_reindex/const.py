# Default Headers for call ElasticSearch API.
HEADERS = {"Content-Type": "application/json"}

# Default arguments for ElasticSearch client init.
DEFAULT_ES_KWARGS = {"max_retries": 3, "timeout": 30, "retry_on_timeout": False}

# Endpoint for create internal ElasticSearch reindex task.
ES_CREATE_TASK_ENDPOINT = "{es_host}/_reindex?pretty&wait_for_completion=false"
ES_CHECK_TASK_ENDPOINT = "{es_host}/_tasks/{task_id}"

# Logging message format.
LOG_FORMAT = "[%(asctime)s] %(message)s"

DEFAULT_CHECK_INTERVAL = 10
DEFAULT_CONCURRENT_TASKS = 1
