"""Helpers for locating GitLab merge request description templates."""

from pathlib import Path

from jyy_amfam_toolkit.constants import MR_TEMPLATE_DIR, MR_TEMPLATE_LEGACY_PATH


def find_templates(repo_root: Path) -> list[Path]:
    """Find available merge request templates in a repository.

    Checks, in order:
      1. Named templates in `.gitlab/merge_request_templates/*.md`
         (GitLab supports multiple; all are returned so the caller can
         prompt for a choice if there's more than one).
      2. The legacy single template at `.gitlab/merge_request_template.md`,
         if no named templates were found.

    Args:
        repo_root: The top-level directory of the git repository.

    Returns:
        A sorted list of template file paths. Empty if none exist.
    """
    templates_dir = repo_root / MR_TEMPLATE_DIR
    if templates_dir.is_dir():
        named_templates = sorted(templates_dir.glob("*.md"))
        if named_templates:
            return named_templates

    legacy_template = repo_root / MR_TEMPLATE_LEGACY_PATH
    if legacy_template.is_file():
        return [legacy_template]

    return []
