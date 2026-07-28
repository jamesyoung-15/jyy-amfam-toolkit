"""The `bookmarks` command group: open user-defined URL bookmarks."""

import webbrowser

import questionary
import typer

from jyy_amfam_toolkit.constants import CONFIG_JSON_PATH
from jyy_amfam_toolkit.core.config import Bookmark, ConfigError, load_config

bookmarks_app = typer.Typer(help="Open user-defined URL bookmarks.")

_BACK = "<- Back"


def _error(message: str) -> None:
    typer.secho(message, fg=typer.colors.RED, err=True)


def _format_bookmark_choice(bookmark: Bookmark) -> str:
    label = bookmark.name
    if bookmark.description:
        label += f" - {bookmark.description}"
    return label


def _folder_names(bookmarks: list[Bookmark]) -> list[str]:
    """Distinct folder names, alphabetically sorted."""
    return sorted({b.folder for b in bookmarks if b.folder is not None})


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

    return config.bookmarks


def _select_from_folder(bookmarks: list[Bookmark], folder: str) -> Bookmark | None:
    """Prompt for a bookmark within a folder. Returns None on 'Back'."""
    folder_bookmarks = [b for b in bookmarks if b.folder == folder]
    choices = [_format_bookmark_choice(b) for b in folder_bookmarks] + [_BACK]

    choice = questionary.select(f"[{folder}] Select a bookmark:", choices=choices).ask()
    if choice is None or choice == _BACK:
        return None

    return folder_bookmarks[choices.index(choice)]


def _select_bookmark(bookmarks: list[Bookmark]) -> Bookmark | None:
    """Top-level navigation: pick a top-level bookmark, or drill into a folder."""
    top_level = [b for b in bookmarks if b.folder is None]
    folders = _folder_names(bookmarks)

    while True:
        top_level_choices = [_format_bookmark_choice(b) for b in top_level]
        folder_choices = [f"[{folder}]" for folder in folders]
        choices = top_level_choices + folder_choices

        choice = questionary.select(
            "Select a bookmark or folder:", choices=choices
        ).ask()
        if choice is None:
            return None

        if choice in folder_choices:
            folder = folders[folder_choices.index(choice)]
            bookmark = _select_from_folder(bookmarks, folder)
            if bookmark is not None:
                return bookmark
            continue

        return top_level[top_level_choices.index(choice)]


@bookmarks_app.command(name="open")
def open_command() -> None:
    """Select a bookmark and open it in the browser."""
    bookmarks = _load_bookmarks()
    if bookmarks is None:
        raise typer.Exit(code=0)

    bookmark = _select_bookmark(bookmarks)
    if bookmark is None:
        raise typer.Exit(code=1)

    typer.echo(bookmark.url)
    webbrowser.open(bookmark.url)
