"""Helpers for extracting Jira ticket references from git branch names."""

import re

from jyy_amfam_toolkit.constants import TICKET_KEY_PATTERN

_TICKET_KEY_RE = re.compile(TICKET_KEY_PATTERN)


def extract_ticket_key(branch_name: str) -> str | None:
    """Extract a Jira ticket key from a branch name.

    Expects branch names following the convention used by the `branch`
    command, e.g. "feat/EITDC-7022-my-slug" -> "EITDC-7022". Also matches
    a bare ticket key anywhere in the branch name.

    Args:
        branch_name: The git branch name to search.

    Returns:
        The extracted ticket key, or None if no key pattern is found
        (e.g. for branches like "main" or "develop").
    """
    if not branch_name:
        return None

    match = _TICKET_KEY_RE.search(branch_name)
    return match.group(0) if match else None
