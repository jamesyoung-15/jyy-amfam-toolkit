"""Tests for converting git remote URLs into browsable web URLs."""

import pytest

from jyy_amfam_toolkit.core.remote_url import extract_project_path, to_web_url


@pytest.mark.parametrize(
    ("remote_url", "expected"),
    [
        # https:// with and without .git suffix
        (
            "https://gitlab.com/user/repo.git",
            "https://gitlab.com/user/repo",
        ),
        (
            "https://gitlab.com/user/repo",
            "https://gitlab.com/user/repo",
        ),
        (
            "https://gitlab.com/group/subgroup/repo.git",
            "https://gitlab.com/group/subgroup/repo",
        ),
        # http:// is preserved as http (no forced https upgrade)
        (
            "http://internal-gitlab.example.com/user/repo.git",
            "http://internal-gitlab.example.com/user/repo",
        ),
        # scp-like syntax: [user@]host:path
        (
            "git@gitlab.com:user/repo.git",
            "https://gitlab.com/user/repo",
        ),
        (
            "git@gitlab.com:group/subgroup/repo.git",
            "https://gitlab.com/group/subgroup/repo",
        ),
        (
            "git@github.com:user/repo.git",
            "https://github.com/user/repo",
        ),
        # scp-like without a user prefix
        (
            "gitlab.com:user/repo.git",
            "https://gitlab.com/user/repo",
        ),
        # ssh:// explicit scheme, with and without port
        (
            "ssh://git@gitlab.com/user/repo.git",
            "https://gitlab.com/user/repo",
        ),
        (
            "ssh://git@gitlab.com:22/user/repo.git",
            "https://gitlab.com/user/repo",
        ),
        (
            "ssh://git@github.com:2222/group/subgroup/repo.git",
            "https://github.com/group/subgroup/repo",
        ),
    ],
)
def test_converts_recognized_remote_urls(remote_url: str, expected: str) -> None:
    assert to_web_url(remote_url) == expected


@pytest.mark.parametrize(
    "remote_url",
    [
        "",
        "   ",
        "/Users/me/repos/my-repo",
        "./relative/path/to/repo",
        "../sibling/repo.git",
        "file:///Users/me/repos/my-repo.git",
        "git://gitlab.com/user/repo.git",
        "C:\\Users\\me\\repo",
    ],
)
def test_returns_none_for_unsupported_or_local_urls(remote_url: str) -> None:
    assert to_web_url(remote_url) is None


def test_strips_surrounding_whitespace() -> None:
    assert (
        to_web_url("  https://gitlab.com/user/repo.git  ")
        == "https://gitlab.com/user/repo"
    )


@pytest.mark.parametrize(
    ("remote_url", "expected"),
    [
        ("https://gitlab.com/user/repo.git", "user/repo"),
        ("https://gitlab.com/group/subgroup/repo.git", "group/subgroup/repo"),
        ("git@gitlab.com:user/repo.git", "user/repo"),
        ("git@gitlab.com:group/subgroup/repo.git", "group/subgroup/repo"),
        ("ssh://git@gitlab.com:22/user/repo.git", "user/repo"),
        ("git@github.com:user/repo.git", "user/repo"),
    ],
)
def test_extract_project_path_returns_namespaced_path(
    remote_url: str, expected: str
) -> None:
    assert extract_project_path(remote_url) == expected


@pytest.mark.parametrize(
    "remote_url",
    [
        "",
        "/Users/me/repos/my-repo",
        "file:///Users/me/repos/my-repo.git",
    ],
)
def test_extract_project_path_returns_none_for_unsupported_urls(
    remote_url: str,
) -> None:
    assert extract_project_path(remote_url) is None
