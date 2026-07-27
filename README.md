# jyy-amfam-toolkit

Personal CLI for automating recurring dev workflow tasks (Jira, git, and
eventually GitLab).

## Prerequisites

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) installed
- `git` available on your PATH
- A Jira Cloud account with an API token
  ([create one here](https://id.atlassian.com/manage-profile/security/api-tokens))

## Setup

1. Clone the repo and install dependencies:

   ```bash
   uv sync
   ```

2. Copy the example env file to `~/.config/jyy-amfam-toolkit/.env` and fill
   in your Jira credentials:

   ```bash
   mkdir -p ~/.config/jyy-amfam-toolkit
   cp .env.example ~/.config/jyy-amfam-toolkit/.env
   ```

   Edit `~/.config/jyy-amfam-toolkit/.env`:

   ```env
   JIRA_URL=https://amfament.atlassian.net
   JIRA_EMAIL=your.email@amfam.com
   JIRA_API_TOKEN=your-api-token-here
   ```

   This fixed location (rather than a `.env` in the project directory) is
   used so the CLI works the same regardless of which directory you run it
   from after a global install. This file is outside the repo and never
   committed.

## Usage

Run commands via `uv run`:

```bash
uv run jyy-amfam-toolkit --help
```

### `branch` — create a git branch from a Jira ticket

Must be run from inside a git repository.

```bash
uv run jyy-amfam-toolkit branch
```

This will:

1. Fetch your Jira tickets (with jql filter set in code)
2. Prompt you to select a ticket.
3. Prompt you to select a [conventional branch](https://conventional-branch.github.io/)
   type (`feat`, `fix`, `chore`, `docs`, `style`, `refactor`, `test`, `build`,
   `ci`, `perf`).
4. Suggest a slug based on the ticket summary (editable).
5. Create and check out a branch named `{type}/{TICKET-KEY}-{slug}`
   (e.g. `feat/EITDC-7022-my-description`).

If the branch already exists locally, you'll be prompted to check it out
instead of erroring.

## Optional: install globally

To run the CLI without prefixing `uv run` every time:

```bash
uv tool install --editable .
```

Then use it directly:

```bash
jyy-amfam-toolkit branch
```

## Development

Make sure to have `pre-commit`. Add `pre-commit` hook:

```bash
pre-commit install
```

This runs `ruff` lint and format checks on git commits.

For unit testing, run:

```bash
uv run pytest
```
