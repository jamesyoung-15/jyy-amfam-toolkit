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

## Other ideas (not yet scoped)

- Optionally transition the Jira ticket status when creating a branch
  (e.g. auto move to "In Progress")
