"""The `dev-servers` command group: browse and check user-defined servers."""

import subprocess

import questionary
import typer

from jyy_amfam_toolkit.constants import CONFIG_JSON_PATH, DEFAULT_PING_TIMEOUT_SECONDS
from jyy_amfam_toolkit.core.config import ConfigError, DevServer, load_config

dev_servers_app = typer.Typer(help="Browse and check user-defined dev servers.")


def _error(message: str) -> None:
    typer.secho(message, fg=typer.colors.RED, err=True)


def _format_server_choice(server: DevServer) -> str:
    label = server.name
    if server.environment:
        label += f" ({server.environment})"
    if server.purpose:
        label += f" - {server.purpose}"
    return label


def _load_servers() -> list[DevServer] | None:
    """Load dev servers, printing a friendly message if config is missing.

    Returns:
        The list of configured servers, or None if the caller should
        exit cleanly (missing config, or config with no servers defined).
    """
    try:
        config = load_config()
    except ConfigError as exc:
        _error(f"Error: {exc}")
        return None

    if config is None or not config.dev_servers:
        typer.echo(
            f"No dev servers configured yet.\n"
            f"Create {CONFIG_JSON_PATH} with a 'dev_servers' list, e.g.:\n\n"
            "{\n"
            '  "dev_servers": [\n'
            '    {"name": "dev-web-1", "address": "10.0.0.5", '
            '"purpose": "web frontend testing", "environment": "dev"}\n'
            "  ]\n"
            "}\n\n"
            "See config.example.json in the repo for the full schema."
        )
        return None

    return config.dev_servers


def _select_server(servers: list[DevServer]) -> DevServer | None:
    choices = [_format_server_choice(server) for server in servers]
    choice = questionary.select("Select a dev server:", choices=choices).ask()
    if choice is None:
        return None
    return servers[choices.index(choice)]


@dev_servers_app.command(name="list")
def list_command() -> None:
    """Select a dev server and show its full details."""
    servers = _load_servers()
    if servers is None:
        raise typer.Exit(code=0)

    server = _select_server(servers)
    if server is None:
        raise typer.Exit(code=1)

    typer.echo(f"Name:        {server.name}")
    typer.echo(f"Address:     {server.address}")
    typer.echo(f"Purpose:     {server.purpose or '(none)'}")
    typer.echo(f"Environment: {server.environment or '(none)'}")


@dev_servers_app.command(name="ping")
def ping_command() -> None:
    """Select a dev server and check connectivity."""
    servers = _load_servers()
    if servers is None:
        raise typer.Exit(code=0)

    server = _select_server(servers)
    if server is None:
        raise typer.Exit(code=1)

    typer.echo(f"Pinging {server.name} ({server.address})...")
    try:
        result = subprocess.run(
            ["ping", "-c", "1", server.address],
            capture_output=True,
            text=True,
            timeout=DEFAULT_PING_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        _error(f"'{server.name}' ({server.address}) is unreachable (timed out).")
        raise typer.Exit(code=1) from None

    if result.returncode == 0:
        typer.secho(
            f"'{server.name}' ({server.address}) is reachable.", fg=typer.colors.GREEN
        )
    else:
        _error(f"'{server.name}' ({server.address}) is unreachable.")
        raise typer.Exit(code=1)


@dev_servers_app.command(name="ssh")
def ssh_command() -> None:
    """Select a dev server and print an SSH command to connect."""
    servers = _load_servers()
    if servers is None:
        raise typer.Exit(code=0)

    server = _select_server(servers)
    if server is None:
        raise typer.Exit(code=1)

    try:
        config = load_config()
    except ConfigError:
        config = None

    ad_username = config.ad_username if config else None
    target = f"{ad_username}@{server.address}" if ad_username else server.address
    typer.echo(f"ssh {target}")
