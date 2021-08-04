from argparse import ArgumentParser


def parser_factory() -> ArgumentParser:
    """
    Create arg parser configured for project.
    """
    parser = ArgumentParser()

    parser.add_argument(
        "--source_host",
        type=str,
        required=True,
        help="Source server: Elasticsearch host where data will be transferred from",
    )
    parser.add_argument(
        "--dest_host",
        type=str,
        required=True,
        help="Destination server: Elasticsearch host where data will be transferred",
    )

    return parser
