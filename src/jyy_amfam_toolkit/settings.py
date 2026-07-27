"""Typed configuration loaded from environment variables / .env file."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from jyy_amfam_toolkit.constants import ENV_FILE


class Settings(BaseSettings):
    """Jira Cloud connection settings.

    Values are loaded from environment variables first, falling back to
    `~/.config/jyy-amfam-toolkit/.env` (see `.env.example` in the repo for
    the expected keys). This fixed location is used (rather than a relative
    `.env` in the current directory) so the CLI works the same regardless
    of which directory it's run from after a global `uv tool install`.
    Never commit a real `.env` file to version control.
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
