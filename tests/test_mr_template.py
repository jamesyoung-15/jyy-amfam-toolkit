"""Tests for locating GitLab merge request templates."""

from pathlib import Path

from jyy_amfam_toolkit.core.mr_template import find_templates


def test_returns_empty_list_when_no_templates_exist(tmp_path: Path) -> None:
    assert find_templates(tmp_path) == []


def test_finds_legacy_single_template(tmp_path: Path) -> None:
    gitlab_dir = tmp_path / ".gitlab"
    gitlab_dir.mkdir()
    legacy_template = gitlab_dir / "merge_request_template.md"
    legacy_template.write_text("## Description\n")

    assert find_templates(tmp_path) == [legacy_template]


def test_finds_single_named_template(tmp_path: Path) -> None:
    templates_dir = tmp_path / ".gitlab" / "merge_request_templates"
    templates_dir.mkdir(parents=True)
    default_template = templates_dir / "Default.md"
    default_template.write_text("## Description\n")

    assert find_templates(tmp_path) == [default_template]


def test_finds_multiple_named_templates_sorted(tmp_path: Path) -> None:
    templates_dir = tmp_path / ".gitlab" / "merge_request_templates"
    templates_dir.mkdir(parents=True)
    bugfix = templates_dir / "Bugfix.md"
    default = templates_dir / "Default.md"
    feature = templates_dir / "Feature.md"
    feature.write_text("feature\n")
    default.write_text("default\n")
    bugfix.write_text("bugfix\n")

    assert find_templates(tmp_path) == [bugfix, default, feature]


def test_prefers_named_templates_over_legacy(tmp_path: Path) -> None:
    gitlab_dir = tmp_path / ".gitlab"
    gitlab_dir.mkdir()
    legacy_template = gitlab_dir / "merge_request_template.md"
    legacy_template.write_text("legacy\n")

    templates_dir = gitlab_dir / "merge_request_templates"
    templates_dir.mkdir()
    named_template = templates_dir / "Default.md"
    named_template.write_text("named\n")

    assert find_templates(tmp_path) == [named_template]


def test_ignores_non_markdown_files_in_templates_dir(tmp_path: Path) -> None:
    templates_dir = tmp_path / ".gitlab" / "merge_request_templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "Default.md").write_text("default\n")
    (templates_dir / "README.txt").write_text("not a template\n")

    result = find_templates(tmp_path)

    assert result == [templates_dir / "Default.md"]


def test_falls_back_to_legacy_when_templates_dir_is_empty(tmp_path: Path) -> None:
    templates_dir = tmp_path / ".gitlab" / "merge_request_templates"
    templates_dir.mkdir(parents=True)

    legacy_template = tmp_path / ".gitlab" / "merge_request_template.md"
    legacy_template.write_text("legacy\n")

    assert find_templates(tmp_path) == [legacy_template]
