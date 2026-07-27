"""Small helpers for git branch operations, shelling out to the git CLI."""

import subprocess


class GitError(Exception):
    """Raised when a git command fails unexpectedly."""


def is_git_repo() -> bool:
    """Return True if the current working directory is inside a git repo."""
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def branch_exists(name: str) -> bool:
    """Return True if a local branch with the given name already exists."""
    result = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{name}"],
        capture_output=True,
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
    )
    if result.returncode != 0:
        raise GitError(result.stderr.strip() or "git checkout failed")
