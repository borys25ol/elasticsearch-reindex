from elasticsearch_reindex.logger import CustomHandler, create_logger


def test_custom_handler_format():
    handler = CustomHandler()
    formatter = handler.formatter
    assert formatter._fmt == "[%(name)s] [%(asctime)s] %(message)s"
    assert formatter.datefmt == "%Y-%m-%dT%T"


def test_create_logger():
    logger1 = create_logger()
    logger2 = create_logger(name="custom_logger")

    assert logger1 is not logger2

    # Test caching: calling create_logger() with the same name should return the same instance.
    logger3 = create_logger()
    assert logger1 is logger3
