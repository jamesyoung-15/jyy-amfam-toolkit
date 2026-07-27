"""CLI entrypoint. Registers all subcommands."""

import typer

from jyy_amfam_toolkit.commands.branch import branch_command
from jyy_amfam_toolkit.commands.jira import jira_app

app = typer.Typer(help="Personal dev workflow automation toolkit.")


@app.callback()
def main() -> None:
    """Personal dev workflow automation toolkit."""


app.command(name="branch")(branch_command)
app.add_typer(jira_app, name="jira")


if __name__ == "__main__":
    app()
