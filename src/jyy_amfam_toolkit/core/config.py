"""User-authored JSON config (dev servers, bookmarks, etc.), separate from
the `.env` secrets file.

Unlike `settings.py` (which reads env vars via pydantic-settings), this
module reads a plain JSON file the user edits by hand. See
`config.example.json` in the repo for the expected shape.
"""

import json
from pathlib import Path

from pydantic import BaseModel, ValidationError

from jyy_amfam_toolkit.constants import CONFIG_JSON_PATH


class ConfigError(Exception):
    """Raised when config.json exists but is malformed or invalid."""


class DevServer(BaseModel):
    """A user-defined dev server entry."""

    name: str
    address: str
    purpose: str | None = None
    environment: str | None = None


class Bookmark(BaseModel):
    """A user-defined URL bookmark entry.

    `folder` groups related bookmarks together for display (e.g. "Datadog").
    None means the bookmark is shown at the top level. Only one level of
    folders is supported (no nested folders).
    """

    name: str
    url: str
    description: str | None = None
    folder: str | None = None


class ToolkitConfig(BaseModel):
    """Top-level shape of config.json."""

    ad_username: str | None = None
    dev_servers: list[DevServer] = []
    bookmarks: list[Bookmark] = []


def load_config(path: Path = CONFIG_JSON_PATH) -> ToolkitConfig | None:
    """Load and validate config.json.

    Args:
        path: Path to the config file. Defaults to the fixed
            `~/.config/jyy-amfam-toolkit/config.json` location.

    Returns:
        The parsed config, or None if the file doesn't exist (an expected
        state on first run, not an error).

    Raises:
        ConfigError: If the file exists but contains invalid JSON or
            doesn't match the expected schema.
    """
    if not path.is_file():
        return None

    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ConfigError(f"{path} contains invalid JSON: {exc}") from exc

    try:
        return ToolkitConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(f"{path} does not match the expected schema:\n{exc}") from exc
