"""
Provide errors for project.
"""
ES_NODE_NOT_FOUND_ERROR = "Can not connect to ElasticSearch server: {host}"
ES_TASK_ID_ERROR = (
    "Can not retrieve task status "
    "from ElasticSearch server: {host} and task id: {task_id}"
)


class BaseCustomException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class ElasticSearchNodeNotFoundException(BaseCustomException):
    """
    Exception raised when Elasticsearch node not found or can not get access.
    """


class ElasticSearchInvalidTaskIDException(BaseCustomException):
    """
    Exception raised when got ElasticSearch invalid task ID.
    """
