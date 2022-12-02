"""Console script for filez_python_sdk."""

import click


@click.command()
def main():
    """Main entrypoint."""
    click.echo("filez-python-sdk")
    click.echo("=" * len("filez-python-sdk"))
    click.echo("Skeleton project created by Cookiecutter PyPackage")


if __name__ == "__main__":
    main()  # pragma: no cover
