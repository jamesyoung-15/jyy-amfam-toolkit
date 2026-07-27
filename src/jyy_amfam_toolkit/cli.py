"""CLI entrypoint. Registers all subcommands."""

import typer

from jyy_amfam_toolkit.commands.branch import branch_command

app = typer.Typer(help="Personal dev workflow automation toolkit.")


@app.callback()
def main() -> None:
    """Personal dev workflow automation toolkit."""


app.command(name="branch")(branch_command)


if __name__ == "__main__":
    app()
