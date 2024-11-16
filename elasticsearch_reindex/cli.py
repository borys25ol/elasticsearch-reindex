import click
from click_default_group import DefaultGroup

from elasticsearch_reindex.manager import Manager


@click.group(cls=DefaultGroup, default="reindex", default_if_no_args=True)
def cli() -> None:
    """
    Main click group.
    """


@cli.command()
@click.option(
    "--source_host",
    required=True,
    type=str,
    help="Source server: Elasticsearch host where data will be transferred from",
)
@click.option(
    "--dest_host",
    required=True,
    type=str,
    help="Destination server: Elasticsearch host where data will be transferred",
)
@click.option(
    "--source_http_auth",
    required=False,
    type=str,
    help="Source server: HTTP Basic authentication, username and password",
)
@click.option(
    "--dest_http_auth",
    required=False,
    type=str,
    help="Destination server: HTTP Basic authentication, username and password",
)
@click.option(
    "--check_interval",
    required=False,
    type=int,
    help="Interval for check Elasticsearch reindex task (in seconds)",
)
@click.option(
    "--concurrent_tasks",
    required=False,
    type=int,
    help="Number of max concurrent reindex tasks",
)
@click.option(
    "--indexes",
    "-i",
    required=False,
    multiple=True,
    help="List of specific Elasticsearch indexes to migrate",
)
def reindex(
    source_host: str,
    dest_host: str,
    source_http_auth: str,
    dest_http_auth: str,
    check_interval: int,
    concurrent_tasks: int,
    indexes: list[str],
) -> None:
    config = {
        "source_host": source_host,
        "dest_host": dest_host,
        "source_http_auth": source_http_auth,
        "dest_http_auth": dest_http_auth,
        "check_interval": check_interval,
        "concurrent_tasks": concurrent_tasks,
        "indexes": list(indexes),
    }
    reindex_manager = Manager.from_dict(data=config)
    reindex_manager.start_reindex()
    click.echo("Success")
