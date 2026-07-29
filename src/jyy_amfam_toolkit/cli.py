"""CLI entrypoint. Registers all subcommands."""

import truststore
import typer

from jyy_amfam_toolkit.commands.bookmarks import bookmarks_app
from jyy_amfam_toolkit.commands.branch import branch_command
from jyy_amfam_toolkit.commands.dev_servers import dev_servers_app
from jyy_amfam_toolkit.commands.glab import glab_app
from jyy_amfam_toolkit.commands.jira import jira_app
from jyy_amfam_toolkit.commands.repo import repo_app

app = typer.Typer(help="Personal dev workflow automation toolkit.")


@app.callback()
def main() -> None:
    """Personal dev workflow automation toolkit."""
    # Use the OS-native certificate trust store instead of certifi's bundled
    # CAs. Needed on networks with a TLS-inspecting proxy (e.g. corporate
    # MITM) whose CA cert isn't in certifi's bundle, which otherwise causes
    # "certificate verify failed" errors on some hosts (observed with
    # GitLab, not Jira -- likely due to different proxy/egress paths).
    # Called here (once, at the application entrypoint) rather than in
    # individual settings/clients, per truststore's own guidance that
    # inject_into_ssl() is for applications, not libraries.
    truststore.inject_into_ssl()


app.command(name="branch")(branch_command)
app.add_typer(bookmarks_app, name="bookmarks")
app.add_typer(dev_servers_app, name="dev-servers")
app.add_typer(glab_app, name="glab")
app.add_typer(jira_app, name="jira")
app.add_typer(repo_app, name="repo")


if __name__ == "__main__":
    app()
