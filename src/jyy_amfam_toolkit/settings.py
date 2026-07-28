"""Typed configuration loaded from environment variables / .env file."""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from jyy_amfam_toolkit.constants import ENV_FILE


class Settings(BaseSettings):
    """Jira Cloud connection settings.

    Values are loaded from environment variables first, falling back to
    `~/.config/jyy-amfam-toolkit/.env`. This fixed location is used so the CLI works the same regardless
    of which directory it's run from after a global `uv tool install`.
    """

    jira_url: str = Field(
        description="Jira Cloud base URL, e.g. https://amfament.atlassian.net"
    )
    jira_email: str = Field(
        description="Email address associated with your Jira Cloud account"
    )
    jira_api_token: str = Field(
        description="Jira API token (create at id.atlassian.com/manage-profile/security/api-tokens)"
    )

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


class GitlabSettings(BaseSettings):
    """GitLab connection settings.

    Kept separate from `Settings` (Jira) so Jira-only usage doesn't require
    GitLab credentials to be configured. Loaded from the same `.env` file.
    """

    gitlab_url: str = Field(
        default="https://gitlab.com",
        description="GitLab base URL, e.g. https://gitlab.com",
    )
    gitlab_token: str = Field(
        description="GitLab personal access token with 'api' scope"
    )

    @field_validator("gitlab_url")
    @classmethod
    def _ensure_scheme(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            return f"https://{value}"
        return value

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )
