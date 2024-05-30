import click
from .functions import fetch_posts_info
from .login import LOGIN


@click.command()
@click.option(
    "-n",
    "--no_of_posts",
    default=5,

)
def fetch(no_of_posts):
    client = LOGIN()
    fetch_posts_info(client, no_of_posts)