"""Tests for extracting Jira ticket keys from git branch names."""

from jyy_amfam_toolkit.core.ticket_ref import extract_ticket_key


def test_extracts_key_from_conventional_branch_with_slug() -> None:
    assert extract_ticket_key("feat/EITDC-7022-my-slug") == "EITDC-7022"


def test_extracts_key_from_conventional_branch_without_slug() -> None:
    assert extract_ticket_key("feat/EITDC-7022") == "EITDC-7022"


def test_extracts_key_with_multi_word_slug() -> None:
    assert (
        extract_ticket_key("fix/EITDC-6805-review-and-exclude-namespaces")
        == "EITDC-6805"
    )


def test_extracts_bare_ticket_key_without_type_prefix() -> None:
    assert extract_ticket_key("EITDC-7022") == "EITDC-7022"


def test_returns_none_for_branch_without_ticket_key() -> None:
    assert extract_ticket_key("main") is None
    assert extract_ticket_key("develop") is None


def test_returns_none_for_empty_string() -> None:
    assert extract_ticket_key("") is None


def test_returns_none_for_branch_with_only_lowercase_words() -> None:
    assert extract_ticket_key("feat/some-random-fix") is None


def test_handles_project_key_with_digits() -> None:
    assert extract_ticket_key("feat/AB123-4567-slug") == "AB123-4567"


def test_extracts_first_match_when_multiple_present() -> None:
    # Branch names shouldn't normally contain two ticket keys, but if they
    # do, extracting the first is a reasonable, well-defined behavior.
    assert extract_ticket_key("feat/EITDC-7022-and-EITDC-7023-slug") == "EITDC-7022"
