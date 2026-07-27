"""Tests for git branch helpers.

These tests exercise real `git` subprocess calls against throwaway
temporary repositories rather than mocking subprocess, since git's actual
CLI behavior (branch refs, checkout semantics) is exactly what we want to
verify.
"""

import os
import subprocess
from collections.abc import Generator
from pathlib import Path

import pytest

from jyy_amfam_toolkit.core import git_utils


@pytest.fixture
def temp_git_repo(tmp_path: Path) -> Generator[Path]:
    """Create a temporary git repo with one commit, and cd into it."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    original_cwd = Path.cwd()
    os.chdir(repo_dir)
    try:
        subprocess.run(["git", "init", "-q"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        (repo_dir / "README.md").write_text("test\n")
        subprocess.run(["git", "add", "README.md"], check=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial commit"], check=True)
        yield repo_dir
    finally:
        os.chdir(original_cwd)


def test_is_git_repo_true_inside_repo(temp_git_repo: Path) -> None:
    assert git_utils.is_git_repo() is True


def test_is_git_repo_false_outside_repo(tmp_path: Path) -> None:
    non_repo_dir = tmp_path / "not-a-repo"
    non_repo_dir.mkdir()

    original_cwd = Path.cwd()
    os.chdir(non_repo_dir)
    try:
        assert git_utils.is_git_repo() is False
    finally:
        os.chdir(original_cwd)


def test_branch_exists_false_for_unknown_branch(temp_git_repo: Path) -> None:
    assert git_utils.branch_exists("does-not-exist") is False


def test_create_branch_then_branch_exists_true(temp_git_repo: Path) -> None:
    git_utils.create_branch("feat/TEST-123-my-slug")
    assert git_utils.branch_exists("feat/TEST-123-my-slug") is True


def test_create_branch_checks_out_new_branch(temp_git_repo: Path) -> None:
    git_utils.create_branch("feat/TEST-123-my-slug")

    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "feat/TEST-123-my-slug"


def test_create_branch_raises_on_duplicate(temp_git_repo: Path) -> None:
    git_utils.create_branch("feat/TEST-123-my-slug")
    subprocess.run(["git", "checkout", "-q", "main"], check=True)

    with pytest.raises(git_utils.GitError):
        git_utils.create_branch("feat/TEST-123-my-slug")


def test_checkout_branch_switches_to_existing_branch(temp_git_repo: Path) -> None:
    git_utils.create_branch("feat/TEST-123-my-slug")
    subprocess.run(["git", "checkout", "-q", "main"], check=True)

    git_utils.checkout_branch("feat/TEST-123-my-slug")

    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "feat/TEST-123-my-slug"


def test_checkout_branch_raises_on_unknown_branch(temp_git_repo: Path) -> None:
    with pytest.raises(git_utils.GitError):
        git_utils.checkout_branch("does-not-exist")


def test_current_branch_returns_checked_out_branch_name(temp_git_repo: Path) -> None:
    git_utils.create_branch("feat/TEST-123-my-slug")
    assert git_utils.current_branch() == "feat/TEST-123-my-slug"


def test_current_branch_reflects_checkout_switch(temp_git_repo: Path) -> None:
    initial_branch = git_utils.current_branch()
    git_utils.create_branch("feat/TEST-123-my-slug")
    git_utils.checkout_branch(initial_branch)

    assert git_utils.current_branch() == initial_branch
