"""
Provide errors for project.
"""
ES_NODE_NOT_FOUND_ERROR = "Can not connect to ElasticSearch server: {host}"
ES_TASK_ID_ERROR = (
    "Can not retrieve task status "
    "from ElasticSearch server: {host} and task id: {task_id}"
)


class ElasticSearchNodeNotFoundException(Exception):
    """
    ElasticSearch node not found or can not get access.
    """

    def __init__(self, message):
        self.message = message


class ElasticSearchInvalidTaskIDException(Exception):
    """
    ElasticSearch invalid task ID.
    """

    def __init__(self, message):
        self.message = message
