"""Tests for typed Jira configuration settings."""

from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from jyy_amfam_toolkit.constants import CONFIG_DIR, ENV_FILE
from jyy_amfam_toolkit.settings import GitlabSettings, Settings


def test_env_file_is_absolute_path_under_home_config_dir() -> None:
    """Regression test.

    Settings previously used a relative ".env" path, which only resolved
    correctly when the CLI was run from inside the project directory. It
    must be an absolute, cwd-independent path so the globally installed
    command works from any directory.
    """
    assert ENV_FILE.is_absolute()
    assert CONFIG_DIR.is_absolute()
    assert ENV_FILE.parent == CONFIG_DIR
    assert ENV_FILE.name == ".env"
    assert str(CONFIG_DIR).startswith(str(Path.home()))
    assert ".config" in CONFIG_DIR.parts
    assert "jyy-amfam-toolkit" in CONFIG_DIR.parts


def test_missing_required_fields_raises_validation_error(monkeypatch) -> None:
    for var in ("JIRA_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"):
        monkeypatch.delenv(var, raising=False)

    # Point at a definitely-nonexistent env file so real user config on the
    # test machine can't accidentally make this pass.
    class NoFileSettings(Settings):
        model_config = SettingsConfigDict(
            env_file="/nonexistent/path/.env", extra="ignore"
        )

    with pytest.raises(ValidationError) as exc_info:
        NoFileSettings()

    missing_fields = {e["loc"][0] for e in exc_info.value.errors()}
    assert missing_fields == {"jira_url", "jira_email", "jira_api_token"}


def test_settings_loaded_from_environment_variables(monkeypatch) -> None:
    monkeypatch.setenv("JIRA_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "me@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "secret-token")

    class NoFileSettings(Settings):
        model_config = SettingsConfigDict(
            env_file="/nonexistent/path/.env", extra="ignore"
        )

    settings = NoFileSettings()

    assert settings.jira_url == "https://example.atlassian.net"
    assert settings.jira_email == "me@example.com"
    assert settings.jira_api_token == "secret-token"


def test_settings_loaded_from_env_file(tmp_path: Path, monkeypatch) -> None:
    for var in ("JIRA_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"):
        monkeypatch.delenv(var, raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text(
        "JIRA_URL=https://fromfile.atlassian.net\n"
        "JIRA_EMAIL=fromfile@example.com\n"
        "JIRA_API_TOKEN=file-token\n"
    )

    class FileSettings(Settings):
        model_config = SettingsConfigDict(env_file=str(env_file), extra="ignore")

    settings = FileSettings()

    assert settings.jira_url == "https://fromfile.atlassian.net"
    assert settings.jira_email == "fromfile@example.com"
    assert settings.jira_api_token == "file-token"


def test_environment_variables_take_priority_over_env_file(
    tmp_path: Path, monkeypatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "JIRA_URL=https://fromfile.atlassian.net\n"
        "JIRA_EMAIL=fromfile@example.com\n"
        "JIRA_API_TOKEN=file-token\n"
    )
    monkeypatch.setenv("JIRA_URL", "https://fromenv.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "fromenv@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "env-token")

    class FileSettings(Settings):
        model_config = SettingsConfigDict(env_file=str(env_file), extra="ignore")

    settings = FileSettings()

    assert settings.jira_url == "https://fromenv.atlassian.net"


def test_gitlab_settings_defaults_to_gitlab_com(monkeypatch) -> None:
    monkeypatch.delenv("GITLAB_URL", raising=False)
    monkeypatch.setenv("GITLAB_TOKEN", "secret-token")

    class NoFileGitlabSettings(GitlabSettings):
        model_config = SettingsConfigDict(
            env_file="/nonexistent/path/.env", extra="ignore"
        )

    settings = NoFileGitlabSettings()

    assert settings.gitlab_url == "https://gitlab.com"


def test_gitlab_settings_requires_token(monkeypatch) -> None:
    monkeypatch.delenv("GITLAB_TOKEN", raising=False)

    class NoFileGitlabSettings(GitlabSettings):
        model_config = SettingsConfigDict(
            env_file="/nonexistent/path/.env", extra="ignore"
        )

    with pytest.raises(ValidationError):
        NoFileGitlabSettings()


def test_gitlab_settings_adds_https_scheme_if_missing(monkeypatch) -> None:
    """Regression test.

    A bare host (e.g. "gitlab.com", no scheme) previously caused httpx
    requests to fail with "missing http:// or https:// protocol" errors.
    """
    monkeypatch.setenv("GITLAB_URL", "gitlab.example.com")
    monkeypatch.setenv("GITLAB_TOKEN", "secret-token")

    class NoFileGitlabSettings(GitlabSettings):
        model_config = SettingsConfigDict(
            env_file="/nonexistent/path/.env", extra="ignore"
        )

    settings = NoFileGitlabSettings()

    assert settings.gitlab_url == "https://gitlab.example.com"


def test_gitlab_settings_preserves_explicit_http_scheme(monkeypatch) -> None:
    monkeypatch.setenv("GITLAB_URL", "http://internal-gitlab.example.com")
    monkeypatch.setenv("GITLAB_TOKEN", "secret-token")

    class NoFileGitlabSettings(GitlabSettings):
        model_config = SettingsConfigDict(
            env_file="/nonexistent/path/.env", extra="ignore"
        )

    settings = NoFileGitlabSettings()

    assert settings.gitlab_url == "http://internal-gitlab.example.com"
