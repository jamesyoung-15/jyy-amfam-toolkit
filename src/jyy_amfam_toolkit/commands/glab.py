"""The `glab` command group: GitLab merge request automation."""

import webbrowser
from pathlib import Path

import httpx
import questionary
import typer
from pydantic import ValidationError

from jyy_amfam_toolkit.constants import ENV_FILE
from jyy_amfam_toolkit.core import git_utils
from jyy_amfam_toolkit.core.gitlab_client import GitlabClient
from jyy_amfam_toolkit.core.jira_client import JiraClient
from jyy_amfam_toolkit.core.mr_template import find_templates
from jyy_amfam_toolkit.core.remote_url import extract_project_path
from jyy_amfam_toolkit.core.ticket_ref import extract_ticket_key
from jyy_amfam_toolkit.settings import GitlabSettings, Settings

glab_app = typer.Typer(help="GitLab-related commands.")
mr_app = typer.Typer(help="Merge request commands.")
glab_app.add_typer(mr_app, name="mr")


def _error(message: str) -> None:
    typer.secho(message, fg=typer.colors.RED, err=True)


def _load_gitlab_settings() -> GitlabSettings | None:
    try:
        return GitlabSettings()
    except ValidationError as exc:
        _error(
            "Error: missing or invalid GitLab configuration.\n"
            f"Create {ENV_FILE} with your GitLab credentials "
            "(see .env.example in the repo for the expected format).\n"
            f"\nDetails:\n{exc}"
        )
        return None


def _resolve_project_path() -> str | None:
    remote_url = git_utils.get_remote_url()
    if remote_url is None:
        _error("Error: no 'origin' remote configured for this repository.")
        return None

    project_path = extract_project_path(remote_url)
    if project_path is None:
        _error(f"Error: could not parse a GitLab project path from '{remote_url}'.")
        return None

    return project_path


def _ensure_branch_pushed(branch: str) -> bool:
    """Ensure the branch has an upstream, pushing it if the user agrees.

    Returns:
        True if the branch has (or now has) an upstream, False if the
        user declined to push or the push failed.
    """
    if git_utils.has_upstream(branch):
        return True

    should_push = questionary.confirm(
        f"Branch '{branch}' hasn't been pushed yet. Push it now?",
        default=True,
    ).ask()
    if not should_push:
        return False

    try:
        git_utils.push_branch(branch)
    except git_utils.GitError as exc:
        _error(f"Error pushing branch: {exc}")
        return False

    return True


def _select_template_description(repo_root: Path) -> str | None:
    """Return description text from a template, or None if none exist."""
    templates = find_templates(repo_root)
    if not templates:
        return None

    if len(templates) == 1:
        chosen = templates[0]
    else:
        choice = questionary.select(
            "Multiple MR templates found. Select one:",
            choices=[t.name for t in templates],
        ).ask()
        if choice is None:
            raise typer.Exit(code=1)
        chosen = next(t for t in templates if t.name == choice)

    return chosen.read_text()


def _build_title(branch: str, jira_settings: Settings | None) -> str | None:
    ticket_key = extract_ticket_key(branch)
    if ticket_key is None or jira_settings is None:
        return questionary.text("MR title:").ask()

    try:
        client = JiraClient(jira_settings)
        summary = None
        for issue in client.search_issues(f'key = "{ticket_key}"', max_results=1):
            summary = issue.summary
    except httpx.HTTPError:
        summary = None

    default_title = f"{ticket_key}: {summary}" if summary else ticket_key
    return questionary.text("MR title:", default=default_title).ask()


def _build_description(ticket_key: str | None, jira_settings: Settings | None) -> str:
    repo_root = git_utils.repo_root()
    if repo_root is not None:
        template_description = _select_template_description(repo_root)
        if template_description is not None:
            return template_description

    if ticket_key and jira_settings is not None:
        return f"Jira: {jira_settings.jira_url.rstrip('/')}/browse/{ticket_key}"

    return ""


@mr_app.command(name="create")
def create_command(
    ready: bool = typer.Option(
        False, "--ready", help="Create as a ready-for-review MR instead of draft."
    ),
) -> None:
    """Create GitLab merge request(s) from the current branch."""
    if not git_utils.is_git_repo():
        _error("Error: not inside a git repository.")
        raise typer.Exit(code=1)

    gitlab_settings = _load_gitlab_settings()
    if gitlab_settings is None:
        raise typer.Exit(code=1)

    project_path = _resolve_project_path()
    if project_path is None:
        raise typer.Exit(code=1)

    branch = git_utils.current_branch()
    if not branch:
        _error("Error: no branch checked out (detached HEAD).")
        raise typer.Exit(code=1)

    if not _ensure_branch_pushed(branch):
        typer.echo("Aborted: branch must be pushed before creating an MR.")
        raise typer.Exit(code=0)

    client = GitlabClient(gitlab_settings)
    try:
        project = client.get_project(project_path)
        branches = client.list_branches(project.id)
    except httpx.HTTPError as exc:
        _error(f"Error communicating with GitLab: {exc}")
        raise typer.Exit(code=1)

    target_choices = [
        questionary.Choice(name, checked=(name == project.default_branch))
        for name in branches
        if name != branch
    ]
    if not target_choices:
        _error("Error: no valid target branches found.")
        raise typer.Exit(code=1)

    target_branches = questionary.checkbox(
        "Select target branch(es) for the MR:", choices=target_choices
    ).ask()
    if not target_branches:
        raise typer.Exit(code=0)

    try:
        jira_settings: Settings | None = Settings()
    except ValidationError:
        jira_settings = None

    ticket_key = extract_ticket_key(branch)
    title = _build_title(branch, jira_settings)
    if not title:
        raise typer.Exit(code=1)
    if not ready:
        title = f"Draft: {title}"

    description = _build_description(ticket_key, jira_settings)

    created_urls: list[str] = []
    for target in target_branches:
        try:
            mr = client.create_merge_request(
                project_id=project.id,
                source_branch=branch,
                target_branch=target,
                title=title,
                description=description,
            )
        except httpx.HTTPError as exc:
            _error(f"Warning: failed to create MR against '{target}': {exc}")
            continue

        typer.secho(
            f"Created MR !{mr.iid} -> {target}: {mr.web_url}", fg=typer.colors.GREEN
        )
        created_urls.append(mr.web_url)

    if not created_urls:
        raise typer.Exit(code=1)

    open_in_browser = questionary.confirm(
        "Open created MR(s) in browser?", default=True
    ).ask()
    if open_in_browser:
        for url in created_urls:
            webbrowser.open(url)
