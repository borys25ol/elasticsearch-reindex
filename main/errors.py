"""
Provide errors for project.
"""
ES_NODE_NOT_FOUND_ERROR = "Can not connect to ElasticSearch server: {host}"


class ElasticSearchNodeNotFoundException(Exception):
    """
    ElasticSearch node not found or can not get access.
    """

    def __init__(self, message):
        self.message = message
