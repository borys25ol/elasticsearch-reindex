from main.manager import Manager
from main.parser import parser_factory


def main() -> None:
    """
    Program entry point.
    """

    parser = parser_factory()
    args = parser.parse_args()

    manager = Manager(args)
    manager.start_reindex()


if __name__ == "__main__":
    main()
