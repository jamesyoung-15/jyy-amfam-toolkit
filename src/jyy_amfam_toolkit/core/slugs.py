"""Slug generation for turning Jira issue summaries into branch-friendly text."""

from slugify import slugify

from jyy_amfam_toolkit.constants import SLUG_MAX_LENGTH


def make_slug(text: str, max_length: int = SLUG_MAX_LENGTH) -> str:
    """Convert free text into a lowercase, hyphenated, length-limited slug.

    Args:
        text: The source text (e.g. a Jira issue summary).
        max_length: Maximum length of the resulting slug.

    Returns:
        A slug suitable for use in a git branch name.
    """
    return slugify(text, max_length=max_length, word_boundary=True, save_order=True)
