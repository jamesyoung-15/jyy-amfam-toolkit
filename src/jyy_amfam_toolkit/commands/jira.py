"""The `jira` command group: browser shortcuts for Jira tickets."""

import webbrowser

import httpx
import questionary
import typer
from pydantic import ValidationError

from jyy_amfam_toolkit.constants import ENV_FILE, JIRA_OPEN_JQL
from jyy_amfam_toolkit.core import git_utils
from jyy_amfam_toolkit.core.jira_client import Issue, JiraClient
from jyy_amfam_toolkit.core.ticket_ref import extract_ticket_key
from jyy_amfam_toolkit.settings import Settings

jira_app = typer.Typer(help="Jira-related commands.")


def _format_issue_choice(issue: Issue) -> str:
    return f"{issue.key} - {issue.summary}"


def _open_ticket_url(jira_url: str, ticket_key: str) -> None:
    url = f"{jira_url.rstrip('/')}/browse/{ticket_key}"
    typer.echo(url)
    webbrowser.open(url)


@jira_app.command(name="open")
def open_command(
    branch: bool = typer.Option(
        False,
        "--branch",
        help="Open the ticket referenced by the current git branch name, "
        "instead of prompting from a list.",
    ),
) -> None:
    """Open a Jira ticket in the browser."""
    try:
        settings = Settings()
    except ValidationError as exc:
        typer.secho(
            "Error: missing or invalid Jira configuration.\n"
            f"Create {ENV_FILE} with your Jira credentials "
            "(see .env.example in the repo for the expected format).\n"
            f"\nDetails:\n{exc}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    if branch:
        if not git_utils.is_git_repo():
            typer.secho(
                "Error: not inside a git repository.", fg=typer.colors.RED, err=True
            )
            raise typer.Exit(code=1)

        current = git_utils.current_branch()
        ticket_key = extract_ticket_key(current)
        if ticket_key is None:
            typer.secho(
                f"Error: could not find a Jira ticket key in branch '{current}'.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)

        _open_ticket_url(settings.jira_url, ticket_key)
        return

    client = JiraClient(settings)
    typer.echo("Fetching Jira tickets...")
    try:
        issues = client.search_issues(JIRA_OPEN_JQL)
    except httpx.HTTPError as exc:
        typer.secho(
            f"Error fetching Jira tickets: {exc}", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)

    if not issues:
        typer.echo("No matching tickets found.")
        raise typer.Exit(code=0)

    issue_choice = questionary.select(
        "Select a Jira ticket:",
        choices=[_format_issue_choice(issue) for issue in issues],
    ).ask()
    if issue_choice is None:
        raise typer.Exit(code=1)
    selected_issue = issues[
        [_format_issue_choice(i) for i in issues].index(issue_choice)
    ]

    _open_ticket_url(settings.jira_url, selected_issue.key)
