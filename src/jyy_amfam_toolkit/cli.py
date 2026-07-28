"""CLI entrypoint. Registers all subcommands."""

import typer

from jyy_amfam_toolkit.commands.branch import branch_command
from jyy_amfam_toolkit.commands.dev_servers import dev_servers_app
from jyy_amfam_toolkit.commands.glab import glab_app
from jyy_amfam_toolkit.commands.jira import jira_app
from jyy_amfam_toolkit.commands.repo import repo_app

app = typer.Typer(help="Personal dev workflow automation toolkit.")


@app.callback()
def main() -> None:
    """Personal dev workflow automation toolkit."""


app.command(name="branch")(branch_command)
app.add_typer(dev_servers_app, name="dev-servers")
app.add_typer(glab_app, name="glab")
app.add_typer(jira_app, name="jira")
app.add_typer(repo_app, name="repo")


if __name__ == "__main__":
    app()
