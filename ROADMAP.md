# Roadmap

Future automations planned for this toolkit. Not yet implemented.

## GitLab MR automation

- Auto-create MR(s) from the current branch
  - Client: [python-gitlab](https://python-gitlab.readthedocs.io/) (direct
    REST API) — targeting gitlab.com
  - Prompt interactively each run for which target branch(es) to create
    MR(s) against (e.g. `main`, `test`) — no fixed global/per-repo config
  - Auto-generate an MR description template, auto-linking the Jira ticket
    (parsed from the current branch name, e.g.
    `feat/EITDC-7022-my-slug` -> `EITDC-7022`)
  - Open questions to resolve when building: MR title format, draft vs.
    ready state, reviewer/assignee defaults, whether to respect an existing
    `.gitlab/merge_request_templates/*.md` if present
- `jyy mr open` — open the GitLab MR for the current branch in the browser
  (find the MR via the GitLab API for the current branch, or fall back to
  prompting if none/multiple exist)

## Jira ticket export

- Pull a ticket's description (and comments, if present) into a local
  markdown/text file for quick reference
  - Jira Cloud returns descriptions in ADF (Atlassian Document Format), not
    plain markdown/HTML — needs an ADF -> markdown renderer (can start
    basic/simplified, expand later)
  - Open question to resolve when building: output location (fixed folder
    vs. cwd vs. prompted each run)

## Other ideas (not yet scoped)

- `jyy jira open` — open the Jira ticket for the current branch in the
  browser (parse ticket key from branch name, build URL from `JIRA_URL`)
- Optionally transition the Jira ticket status when creating a branch
  (e.g. auto move to "In Progress")
