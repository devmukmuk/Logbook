# Logbook

Pilot logbook tools: military flight time conversions, commercial/ATP and
medical tracking, job application and resume support, and importers for
existing logbooks. Everything runs locally: a **dashboard server** in the
browser and a **`logbook` CLI** for the Python tools.

> **This repository is public.** Your logbook data never goes in it. All
> personal files live in a git-ignored data folder (see [Data](#data)).

## Setup

Needs Python 3.12+ (developed on 3.14). From Git Bash in the repository root:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install --upgrade pip
.venv/Scripts/python -m pip install -e ".[dev]"
tools/git-hooks/install.sh
```

On macOS/Linux the venv path is `.venv/bin/` instead of `.venv/Scripts/`.

## Use

```bash
.venv/Scripts/logbook --help          # list the tools
.venv/Scripts/logbook serve --open    # dashboard on http://127.0.0.1:8765/
.venv/Scripts/logbook paths           # where your data is kept
```

`python -m logbook ...` works too. Once the venv is activated
(`source .venv/Scripts/activate`), plain `logbook ...` is enough.

The dashboard binds to `127.0.0.1` only and has no login: it is a
single-user tool for this computer. The JSON API is documented at
`/api/docs` while the server runs.

## Data

| Folder | Holds |
|---|---|
| `data/` | everything personal (git-ignored) |
| `data/imports/` | raw files from other logbooks, as received |
| `data/exports/` | summaries and breakdowns Logbook generates |
| `data/logs/` | run logs |

Set `LOGBOOK_DATA_DIR` to keep the data folder somewhere else, such as an
encrypted vault. The pre-commit hook refuses data folders, spreadsheets and
documents (`.csv`, `.xlsx`, `.pdf`, `.docx`, ...) outside `tests/fixtures/`
and `docs/`.

## Tests

```bash
.venv/Scripts/python -m pytest
```

## Project docs

- [docs/design/](docs/design/): architecture, features and open questions
- [docs/epics/](docs/epics/README.md): epic codes used in commits, branches and issue labels
- [tools/](tools/README.md): git workflow docs (ChangeIt / FinishIt / PostMerge), hooks, label script
