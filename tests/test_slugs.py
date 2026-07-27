"""Tests for slug generation."""

from jyy_amfam_toolkit.core.slugs import make_slug


def test_basic_summary_is_slugified() -> None:
    assert make_slug("Fix login page redirect bug") == "fix-login-page-redirect-bug"


def test_special_characters_are_stripped() -> None:
    assert make_slug("Weird!! Chars @@ ## in $$ Summary") == "weird-chars-in-summary"


def test_mixed_case_is_lowercased() -> None:
    assert make_slug("Fix Login Page") == "fix-login-page"


def test_empty_string_returns_empty_slug() -> None:
    assert make_slug("") == ""


def test_long_summary_is_truncated_at_word_boundary_preserving_order() -> None:
    """Regression test.

    python-slugify's word_boundary truncation reorders/picks words out of
    sequence unless save_order=True is also passed. Without it, this exact
    input previously produced 'this-is-a-really-long-summary-that-get-a'
    (note: dropped "should", jumbled tail) instead of a clean prefix.
    """
    text = (
        "This is a really long summary that should get truncated at a "
        "word boundary nicely"
    )
    result = make_slug(text, max_length=40)

    assert result == "this-is-a-really-long-summary-that"
    assert len(result) <= 40
    # Ensure result is a clean prefix of the words in original order, not a
    # scrambled subset.
    assert text.lower().replace(" ", "-").startswith(result)


def test_max_length_is_respected_for_short_text() -> None:
    result = make_slug("Fix bug", max_length=5)
    assert len(result) <= 5


def test_custom_max_length_truncates_differently_than_default() -> None:
    text = "Fix login page redirect bug across all environments"
    short = make_slug(text, max_length=10)
    long = make_slug(text, max_length=40)

    assert len(short) <= 10
    assert len(long) <= 40
    assert len(short) < len(long)
