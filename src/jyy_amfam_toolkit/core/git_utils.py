"""Small helpers for git branch operations, shelling out to the git CLI."""

import subprocess
from pathlib import Path


class GitError(Exception):
    """Raised when a git command fails unexpectedly."""


def is_git_repo() -> bool:
    """Return True if the current working directory is inside a git repo."""
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def current_branch() -> str:
    """Return the name of the currently checked-out branch.

    Returns an empty string if in a detached HEAD state (no branch
    checked out).
    """
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def branch_exists(name: str) -> bool:
    """Return True if a local branch with the given name already exists."""
    result = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{name}"],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def create_branch(name: str) -> None:
    """Create and check out a new branch.

    Raises:
        GitError: If the git command fails.
    """
    result = subprocess.run(
        ["git", "checkout", "-b", name],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise GitError(result.stderr.strip() or "git checkout -b failed")


def checkout_branch(name: str) -> None:
    """Check out an existing branch.

    Raises:
        GitError: If the git command fails.
    """
    result = subprocess.run(
        ["git", "checkout", name],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise GitError(result.stderr.strip() or "git checkout failed")


def get_remote_url(remote_name: str = "origin") -> str | None:
    """Return the URL of a git remote, or None if it doesn't exist.

    A missing remote is a common, expected case (e.g. a local-only repo
    with no remote configured), so this returns None rather than raising.
    """
    result = subprocess.run(
        ["git", "remote", "get-url", remote_name],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return None

    return result.stdout.strip()


def repo_root() -> Path | None:
    """Return the top-level directory of the current git repository.

    Returns None if not inside a git repository.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return None

    return Path(result.stdout.strip())


def has_upstream(branch: str) -> bool:
    """Return True if the given branch has a remote tracking branch."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def push_branch(branch: str, remote: str = "origin") -> None:
    """Push a branch to a remote, setting it as the upstream tracking branch.

    Raises:
        GitError: If the git command fails.
    """
    result = subprocess.run(
        ["git", "push", "--set-upstream", remote, branch],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise GitError(result.stderr.strip() or "git push failed")
