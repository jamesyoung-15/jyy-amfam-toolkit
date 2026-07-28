# Roadmap

Future automations planned for this toolkit. Not yet implemented.

## Jira ticket export

- Pull a ticket's description (and comments, if present) into a local
  markdown/text file for quick reference
  - Jira Cloud returns descriptions in ADF (Atlassian Document Format), not
    plain markdown/HTML — needs an ADF -> markdown renderer (can start
    basic/simplified, expand later)
  - Open question to resolve when building: output location (fixed folder
    vs. cwd vs. prompted each run)

## URL Bookmarks

- Using user defined config, basically show list of bookmarks with brief summary (what the url is/goes to), user selects it and it launches in browser
- Builds on the `dev_servers`-style config already in `core/config.py`
  (`~/.config/jyy-amfam-toolkit/config.json`) — add a `bookmarks` section
  to the same file rather than a separate config
- Nice to have:
  - tree-like structure, so can have "folder" bookmark, limit perhaps to 2 levels right now

## Other ideas (not yet scoped)

- Optionally transition the Jira ticket status when creating a branch
  (e.g. auto move to "In Progress")
