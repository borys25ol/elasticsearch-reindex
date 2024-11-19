from elasticsearch_reindex.errors import (
    ES_NODE_NOT_FOUND_ERROR,
    ES_TASK_ID_ERROR,
    BaseCustomException,
    ElasticSearchInvalidTaskIDException,
    ElasticSearchNodeNotFoundException,
)


def test_base_custom_exception():
    message = "Test base exception message"
    exception = BaseCustomException(message)
    assert str(exception) == message
    assert exception.message == message


def test_elasticsearch_node_not_found_exception():
    message = "Elasticsearch node not found"
    exception = ElasticSearchNodeNotFoundException(message)
    assert str(exception) == message
    assert exception.message == message


def test_elasticsearch_invalid_task_id_exception():
    message = "Invalid task ID provided"
    exception = ElasticSearchInvalidTaskIDException(message)
    assert str(exception) == message
    assert exception.message == message


def test_es_node_not_found_error_message():
    host = "http://localhost:9200"
    expected_message = f"Can not connect to ElasticSearch server: {host}"
    assert ES_NODE_NOT_FOUND_ERROR.format(host=host) == expected_message


def test_es_task_id_error_message():
    host = "http://localhost:9200"
    task_id = "123"
    expected_message = f"Can not retrieve task status from ElasticSearch server: {host} and task id: {task_id}"
    assert ES_TASK_ID_ERROR.format(host=host, task_id=task_id) == expected_message
