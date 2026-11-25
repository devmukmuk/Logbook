# Architecture

Status: **Accepted** (2026-11-25)

## Goals

- One Python package, `logbook`, holding all logic.
- Two front ends over that package: a **local dashboard server** for looking
  at the data, and a **CLI** for running tools (import, convert, export).
- Personal data never enters the repository, which is public.

## Stack

| Piece | Choice | Why |
|---|---|---|
| Language | Python 3.12+ in a project `.venv` | matches the other tools; good CSV/spreadsheet libraries |
| Packaging | `pyproject.toml`, installed editable (`pip install -e ".[dev]"`) | gives the `logbook` command on the venv's PATH |
| CLI | `argparse` subcommands (`logbook <tool>`) | standard library, no extra dependency |
| Server | FastAPI + uvicorn | small, typed JSON API with built-in docs at `/api/docs` |
| Pages | Jinja2 templates + one CSS file | server-rendered, no JavaScript build step |
| Charts | not chosen yet | decide with the first chart (DASH epic) |
| Tests | pytest; FastAPI `TestClient` for the server | |

## Layout

```
logbook/                 the package
  cli.py                 `logbook` command; one function per subcommand
  config.py              data folder paths, host/port defaults
  server/
    app.py               FastAPI app factory (create_app)
    templates/           Jinja2 pages
    static/              CSS (and later JS/images)
tests/                   pytest; conftest.py points LOGBOOK_DATA_DIR at a temp folder
docs/design/             design docs (this folder)
docs/epics/              epic registry docs
config/git/epics.txt     epic codes (source of truth for hooks and labels)
tools/                   dev workflow docs, git hooks, label script
```

As features land, logic goes in modules beside `cli.py` (for example
`logbook/model.py`, `logbook/importers/`, `logbook/conversions/`). The CLI and
the server stay thin: both call the same functions, so a total shown on the
dashboard and one printed by the CLI cannot disagree.

## Data folder

All personal data lives in one folder, `data/` at the repository root by
default (git-ignored), with `imports/`, `exports/` and `logs/` under it.
`LOGBOOK_DATA_DIR` moves it anywhere, for example into an encrypted vault.
`logbook paths` shows the current location.

Three layers keep data out of git:

1. `.gitignore` ignores `data/`, `imports/`, `exports/`, `logs/` and `.env*`.
2. The pre-commit hook (`tools/git-hooks/check-data-files.sh`) refuses those
   folders plus any spreadsheet or document (`.csv .xlsx .pdf .docx` ...)
   outside `tests/fixtures/`, `logbook/templates/` and `docs/`.
3. `tests/test_check_data_files.py` runs the same check on every tracked file,
   as a backstop for a skipped hook.

Test fixtures use invented flights only.

## Server

- `logbook serve` runs uvicorn on `127.0.0.1:8765`. `--open` opens a browser,
  `--reload` restarts on code changes.
- No authentication: it is single-user and local. Binding to anything other
  than `127.0.0.1` would expose the logbook to the network. Don't do it
  without adding a login first.
- `/` is the dashboard; `/api/health` and `/api/summary` are JSON; `/api/docs`
  is the interactive API reference.

## CLI

- `logbook <command>`, where each tool is a `_cmd_<name>` function registered
  in `build_parser()`.
- Current commands: `version`, `paths [--create]`, `serve`.
- Commands that change data should offer `--dry-run`.
