"""The `branch` command: pick a Jira ticket and create a conventional git branch."""

import httpx
import questionary
import typer
from pydantic import ValidationError

from jyy_amfam_toolkit.core import git_utils
from jyy_amfam_toolkit.core.jira_client import Issue, JiraClient
from jyy_amfam_toolkit.core.slugs import make_slug
from jyy_amfam_toolkit.settings import Settings

JQL = "assignee = currentUser() AND status != Done ORDER BY updated DESC"

BRANCH_TYPES = [
    "feat",
    "fix",
    "chore",
    "docs",
    "style",
    "refactor",
    "test",
    "build",
    "ci",
    "perf",
]


def _format_issue_choice(issue: Issue) -> str:
    return f"{issue.key} - {issue.summary}"


def branch_command() -> None:
    """Create a git branch from a Jira ticket using a conventional-branch prefix."""
    if not git_utils.is_git_repo():
        typer.secho(
            "Error: not inside a git repository.", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)

    try:
        settings = Settings()
    except ValidationError as exc:
        typer.secho(
            "Error: missing or invalid Jira configuration.\n"
            "Copy .env.example to .env and fill in your Jira credentials.\n"
            f"\nDetails:\n{exc}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    client = JiraClient(settings)
    typer.echo("Fetching Jira tickets...")
    try:
        issues = client.search_issues(JQL)
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

    branch_type = questionary.select(
        "Select a branch type:", choices=BRANCH_TYPES
    ).ask()
    if branch_type is None:
        raise typer.Exit(code=1)

    default_slug = make_slug(selected_issue.summary)
    slug = questionary.text("Slug:", default=default_slug).ask()
    if slug is None:
        raise typer.Exit(code=1)
    slug = slug.strip()

    branch_name = (
        f"{branch_type}/{selected_issue.key}-{slug}"
        if slug
        else f"{branch_type}/{selected_issue.key}"
    )

    if git_utils.branch_exists(branch_name):
        checkout = questionary.confirm(
            f"Branch '{branch_name}' already exists. Check it out instead?",
            default=True,
        ).ask()
        if not checkout:
            raise typer.Exit(code=0)
        try:
            git_utils.checkout_branch(branch_name)
        except git_utils.GitError as exc:
            typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)
        typer.secho(
            f"Checked out existing branch: {branch_name}", fg=typer.colors.GREEN
        )
        return

    try:
        git_utils.create_branch(branch_name)
    except git_utils.GitError as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    typer.secho(f"Created and checked out branch: {branch_name}", fg=typer.colors.GREEN)
