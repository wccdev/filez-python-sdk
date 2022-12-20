"""Console script for filez."""

import click


@click.command()
def main():
    """Main entrypoint."""
    click.echo("filez")
    click.echo("=" * len("filez"))
    click.echo("filez")


if __name__ == "__main__":
    main()  # pragma: no cover
