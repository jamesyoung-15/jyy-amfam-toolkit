"""Typed configuration loaded from environment variables / .env file."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Jira Cloud connection settings.

    Values are loaded from environment variables first, falling back to a
    local `.env` file (see `.env.example` for the expected keys). Never
    commit a real `.env` file to version control.
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
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
