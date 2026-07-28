"""The `bookmarks` command group: open user-defined URL bookmarks."""

import webbrowser

import questionary
import typer

from jyy_amfam_toolkit.constants import CONFIG_JSON_PATH
from jyy_amfam_toolkit.core.config import Bookmark, ConfigError, load_config

bookmarks_app = typer.Typer(help="Open user-defined URL bookmarks.")


def _error(message: str) -> None:
    typer.secho(message, fg=typer.colors.RED, err=True)


def _format_bookmark_choice(bookmark: Bookmark) -> str:
    label = f"[{bookmark.folder}] {bookmark.name}" if bookmark.folder else bookmark.name
    if bookmark.description:
        label += f" - {bookmark.description}"
    return label


def _sorted_bookmarks(bookmarks: list[Bookmark]) -> list[Bookmark]:
    """Order bookmarks for display: top-level first (original order), then
    remaining bookmarks grouped by folder name (alphabetical), preserving
    original order within each folder.
    """
    top_level = [b for b in bookmarks if b.folder is None]
    foldered = [b for b in bookmarks if b.folder is not None]
    foldered.sort(key=lambda b: b.folder or "")
    return top_level + foldered


def _load_bookmarks() -> list[Bookmark] | None:
    """Load bookmarks, printing a friendly message if config is missing.

    Returns:
        The list of configured bookmarks, or None if the caller should
        exit cleanly (missing config, or config with no bookmarks defined).
    """
    try:
        config = load_config()
    except ConfigError as exc:
        _error(f"Error: {exc}")
        return None

    if config is None or not config.bookmarks:
        typer.echo(
            f"No bookmarks configured yet.\n"
            f"Create {CONFIG_JSON_PATH} with a 'bookmarks' list, e.g.:\n\n"
            "{\n"
            '  "bookmarks": [\n'
            '    {"name": "Company Wiki", "url": "https://wiki.example.com", '
            '"description": "internal wiki"}\n'
            "  ]\n"
            "}\n\n"
            "See config.example.json in the repo for the full schema."
        )
        return None

    return _sorted_bookmarks(config.bookmarks)


@bookmarks_app.command(name="open")
def open_command() -> None:
    """Select a bookmark and open it in the browser."""
    bookmarks = _load_bookmarks()
    if bookmarks is None:
        raise typer.Exit(code=0)

    choices = [_format_bookmark_choice(bookmark) for bookmark in bookmarks]
    choice = questionary.select("Select a bookmark:", choices=choices).ask()
    if choice is None:
        raise typer.Exit(code=1)

    bookmark = bookmarks[choices.index(choice)]
    typer.echo(bookmark.url)
    webbrowser.open(bookmark.url)
