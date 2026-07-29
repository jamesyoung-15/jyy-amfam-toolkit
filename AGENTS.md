# Agent.md

Instructions for coding agents.

## Project Overview

This is my personal AIO dev shortcuts for automating basic dev workflows via CLI. Examples include creating git branch from Jira ticket, create and auto-fill Gitlab MR, etc..

## Coding Standards

- Always run lint and formatting checks after code edits with `uv run ruff check <file_path>` and `uv run ruff format <file_path>`
- Comment sparingly, code says what, comments explain non-obvious behaviour. Add docstrings to functions and classes
- Breakdown changes into small commits, avoid single large commit
- Commit messages follows conventional commit (eg. `feat: login authenication`), keep commit message informative and brief
