"""The `repo` command group: browser shortcuts for the current repository."""

import webbrowser

import typer

from jyy_amfam_toolkit.core import git_utils
from jyy_amfam_toolkit.core.remote_url import to_web_url

repo_app = typer.Typer(help="Repository-related commands.")


@repo_app.command(name="open")
def open_command(
    remote: str = typer.Option(
        "origin", "--remote", help="Name of the git remote to open."
    ),
) -> None:
    """Open the current repository's remote page in the browser."""
    if not git_utils.is_git_repo():
        typer.secho(
            "Error: not inside a git repository.", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)

    remote_url = git_utils.get_remote_url(remote)
    if remote_url is None:
        typer.echo(
            f"No '{remote}' remote configured for this repository. Nothing to open."
        )
        raise typer.Exit(code=0)

    web_url = to_web_url(remote_url)
    if web_url is None:
        typer.echo(
            f"Remote '{remote}' ({remote_url}) doesn't look like a browsable "
            "URL. Nothing to open."
        )
        raise typer.Exit(code=0)

    typer.echo(web_url)
    webbrowser.open(web_url)
