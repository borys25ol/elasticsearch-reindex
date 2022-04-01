"""
Variables for testing.
"""
import os

TEST_ENV = os.getenv("ENV") == "test"

ES_SOURCE_HOST = os.getenv("LOCAL_IP")
ES_SOURCE_PORT = os.getenv("ES_SOURCE_PORT")
ES_DEST_PORT = os.getenv("ES_DEST_PORT")

LOCAL_SOURCE_HOST = f"http://{ES_SOURCE_HOST}:{ES_SOURCE_PORT}"
LOCAL_DEST_HOST = f"http://{ES_SOURCE_HOST}:{ES_DEST_PORT}"

# Elasticsearch test index.
ES_TEST_INDEX = "test_index_{number}"
