"""
Provides a CLI for client interactions with services.

Built using click. References:
- https://click.palletsprojects.com/en/8.1.x/commands/

"""

import click
from typing import Optional

from pubsub_demo.client import StampsApi


@click.group()
def stamps():
    pass


@stamps.command()
@click.argument("type")
@click.argument("num")
@click.option("--id", "id")
def request(type: str, num: int, id: Optional[str] = None):
    api = StampsApi()
    resp = api.create_stamps(type=type, num=num, id=id)
    click.echo(f"Response: {resp}")


@stamps.command()
@click.option("--id", "id")
def retrieve(id: Optional[str] = None):
    api = StampsApi()
    resp = api.retrieve_stamps(id=id)
    click.echo(f"Response: {resp}")


def main():
    stamps()


if __name__ == "__main__":
    main()
