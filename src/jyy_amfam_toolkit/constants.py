"""Shared constants used across the toolkit.

Centralized here so common tweaks (JQL filters, branch type list, Jira API
config, config file location) don't require hunting through multiple
modules.
"""

from pathlib import Path

# --- Jira API ---

JIRA_SEARCH_PATH = "/rest/api/3/search/jql"
JIRA_REQUEST_TIMEOUT_SECONDS = 15.0

# --- `branch` command ---

# JQL used to list candidate tickets for the `branch` command.
BRANCH_JQL = "assignee = currentUser() AND status NOT IN (Done,Cancelled,Waiting) ORDER BY updated DESC"

# JQL used to list candidate tickets for the `jira open` command. Slightly
# broader than BRANCH_JQL since browsing to view a ticket doesn't imply
# you're about to start work on it (e.g. Waiting tickets are included).
JIRA_OPEN_JQL = (
    "assignee = currentUser() AND status NOT IN (Done,Cancelled) ORDER BY updated DESC"
)

# Regex for extracting a Jira ticket key (e.g. "EITDC-7022") from a git
# branch name such as "feat/EITDC-7022-my-slug".
TICKET_KEY_PATTERN = r"[A-Z][A-Z0-9]+-\d+"

# Conventional branch (https://conventional-branch.github.io/) type prefixes
# offered when creating a branch.
CONVENTIONAL_BRANCH_TYPES = [
    "feat",
    "fix",
    "chore",
    "docs",
    "style",
    "refactor",
    "test",
    "build",
    "ci",
    "perf",
]

# --- Slugs ---

SLUG_MAX_LENGTH = 100

# --- Config file location ---

# Fixed, cwd-independent location so the CLI behaves the same regardless of
# which directory it's run from after a global `uv tool install`.
CONFIG_DIR = Path.home() / ".config" / "jyy-amfam-toolkit"
ENV_FILE = CONFIG_DIR / ".env"
