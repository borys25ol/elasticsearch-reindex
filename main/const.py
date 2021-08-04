import os

from dotenv import load_dotenv

load_dotenv()

# Default Headers for call ElasticSearch API.
HEADERS = {
    "Content-Type": "application/json",
}

# Endpoint for create internal ElasticSearch reindex task.
ES_CREATE_TASK_ENDPOINT = "{es_host}/_reindex?pretty&wait_for_completion=false"
ES_CHECK_TASK_ENDPOINT = "{es_host}/_tasks/{task_id}"

# Elasticsearch test index.
ES_TEST_INDEX = "test_index"

# Logging message format.
LOG_FORMAT = "%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s"

# Variables for testing.
TEST_ENV = os.getenv("ENV") == "test"
ES_SOURCE_HOST = os.getenv("LOCAL_HOST")
ES_SOURCE_PORT = os.getenv("ES_SOURCE_PORT")
