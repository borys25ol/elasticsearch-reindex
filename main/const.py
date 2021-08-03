# Default Headers for call ElasticSearch API.
HEADERS = {
    "Content-Type": "application/json",
}

# Endpoint for create internal ElasticSearch reindex task.
ES_TASK_API_URL = "{es_host}/_reindex?pretty&wait_for_completion=false"

# Elasticsearch test index.
ES_TEST_INDEX = "test_index"

# Logging message format.
LOG_FORMAT = "%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s"
