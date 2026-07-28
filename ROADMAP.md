# Roadmap

Future automations planned for this toolkit. Not yet implemented.

## GitLab MR automation

- `jyy glab mr open` — open the GitLab MR for the current branch in the
  browser (find the MR via the GitLab API for the current branch, or fall
  back to prompting if none/multiple exist)

## Jira ticket export

- Pull a ticket's description (and comments, if present) into a local
  markdown/text file for quick reference
  - Jira Cloud returns descriptions in ADF (Atlassian Document Format), not
    plain markdown/HTML — needs an ADF -> markdown renderer (can start
    basic/simplified, expand later)
  - Open question to resolve when building: output location (fixed folder
    vs. cwd vs. prompted each run)

## List and Access Dev Servers

- User defines a list of servers, either their raw IP or hostname (eg. in a config file or just a plain text) with optional metadata (eg. server purpose, environment, etc.)
- `jyy dev-servers list` - shows list of servers (with perhaps brief metadata), if user chooses a server then it dumps full metadata
- `jyy dev-servers ping` - ping a host to check connectivity
- Nice to haves:
  - `jyy dev-servers ssh` - shows list of servers, user chooses server then it will perform an SSH command (perhaps need another shell, tmux, or just print out ssh command for user to copy paste)

## URL Bookmarks

- Using user defined config, basically show list of bookmarks with brief summary (what the url is/goes to), user selects it and it launches in browser
- Nice to have:
  - tree-like structure, so can have "folder" bookmark, limit perhaps to 2 levels right now

## YAML/JSON Config

- Add a YAML/JSON config (more likely json) alongside `.env` for user defined helpful notes like:
  - user's active directory username (our org uses for ssh/remote access)
  - list of dev servers (see above)
  - bookmarked urls with metadata (eg. datadog url, infoblox url, etc.) as these sometimes have weird hostname and are hard to remember, basically act as browser bookmark but in cli (see above)

## Other ideas (not yet scoped)

- Optionally transition the Jira ticket status when creating a branch
  (e.g. auto move to "In Progress")
