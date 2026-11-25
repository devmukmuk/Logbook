# Logbook Epics

The codes below are the registry read from `config/git/epics.txt` and enforced
by the `commit-msg` and `pre-push` git hooks in `tools/git-hooks/` (see that
folder's `install.sh`).

The split follows the repository's purpose: a pilot logbook, military time
conversions, certificate and medical tracking, career support, and import tools,
all shown on a local dashboard and driven from a CLI. Expect it to change as
real scope lands. When an area needs its own bucket, add a code to
`config/git/epics.txt` and a row here.

| Label | Code | Epic | Covers |
|-------|------|------|--------|
| `Epic-01-DATA` | DATA | Logbook Data Model & Storage | flight entry model, aircraft, totals, storage format, data folder, backups |
| `Epic-02-IMP` | IMP | Import Tools | importers for other logbooks (CSV/spreadsheet exports, military records), mapping, duplicate detection, dry-run |
| `Epic-03-CONV` | CONV | Military Conversions | military flight time to civil (FAA) categories: PIC/SIC, cross-country, night, instrument, sorties to landings |
| `Epic-04-CERT` | CERT | Certificates, Ratings & Medical | ATP / commercial requirement progress (14 CFR 61), ratings, medical class and expiry, currency |
| `Epic-05-CAR` | CAR | Career Support | job application time summaries, airline-style hour breakdowns, resume support |
| `Epic-06-DASH` | DASH | Dashboard Server | local web server, dashboard pages, charts, API endpoints |
| `Epic-07-CLI` | CLI | Command-Line Tools | the `logbook` command and its subcommands |
| `Epic-08-DEV` | DEV | Dev Environment & Tooling | `.venv`, `pyproject.toml`, tests, git hooks, CI, `tools/` |
| `Epic-09-DOC` | DOC | Documentation | `docs/`, `README.md`, `CLAUDE.md` |

## Issues and labels

Every issue names its epic **when the epic is known**:

- the first line of the issue body is `**Epic:** <CODE>` (e.g. `**Epic:** DATA`)
- the issue carries the matching label `Epic-<NN>-<CODE>` (e.g. `Epic-01-DATA`, `Epic-02-IMP`), so the backlog can be filtered by epic on GitHub

If the epic is not yet known, leave both off and add them once it is.

The label number is the position of the code in `config/git/epics.txt`
(DATA is the first line, so `Epic-01-DATA`). Append new epics at the end and
never reorder them, so existing labels stay valid. `tools/epic-labels.sh`
creates or updates the labels from that file and is safe to re-run.

## Suggested build order

1. **DEV**: scaffold, venv, hooks, tests (this setup).
2. **DATA**: flight entry model and storage, once the open questions in [design/FEATURES.md](../design/FEATURES.md#open-questions) are answered.
3. **IMP**: the first importer, for whatever logbook the existing hours live in today.
4. **CONV**: military conversion rules applied during or after import.
5. **DASH** and **CLI**: totals and breakdowns over real data.
6. **CERT**, then **CAR**: requirement progress, then application-ready summaries.

## Conventions enforced by the git hooks

**Commit subject:**
```
<type>(<CODE>): <short description>
```
Example: `feat(DATA): add flight entry model`

**Branch name:**
```
<type>/<issue>-<CODE>-<short-description>
```
Example: `feat/12-DATA-add-flight-entry-model`

**Allowed types:** `feat fix docs test refactor perf build chore`

**Main branch:** `commit-msg` blocks commits on `main`; `pre-push` blocks pushes
to `main`. Every change goes through issue → branch → pull request.
