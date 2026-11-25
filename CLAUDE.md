# Logbook

Pilot logbook: Python package `logbook/` with a local dashboard server (FastAPI + Jinja2, `logbook serve`) and a CLI (`logbook <command>`, argparse). Design: `docs/design/` (ARCHITECTURE.md accepted; FEATURES.md draft with open questions Q1-Q5).

## Where things live
- Dev repo: `E:\dev\repos\github.com\devmukmuk\Logbook` (git, `origin` = https://github.com/devmukmuk/Logbook.git, **public**, branch `main`).
- The `E:\` drive root is a separate personal-workflows repo that ignores `dev/repos/`, so this repo tracks independently.
- Package: `logbook/` (`cli.py`, `config.py`, `server/`). Tests: `tests/`. Design docs: `docs/design/`.

## Rules
- **No personal data in git, ever: the repo is public.** Logbook entries, imports, medicals, certificates, resumes and employer details live only in the data folder (`data/` git-ignored, or `LOGBOOK_DATA_DIR`). The pre-commit hook (`tools/git-hooks/check-data-files.sh`) refuses data folders, spreadsheets and documents; never `--no-verify` around it. Fixtures use invented flights only.
- **Never commit directly to `main`.** Every change is issue -> branch -> PR. Hooks in `tools/git-hooks/` enforce it (run `tools/git-hooks/install.sh` once per clone; re-run after any change under `tools/git-hooks/`).
- On "changeit" / "finishit" / "postmerge", read the matching `tools/dev-docs/*.md` first and follow it. FinishIt ends with 3 beeps via the **PowerShell** tool (Bash has no audio).
- Commit subject `<type>(<EPIC>): desc`; branch `<type>/<issue>-<EPIC>-desc`. Epic codes: `config/git/epics.txt` (DATA IMP CONV CERT CAR DASH CLI DEV DOC, in label-number order); meanings in `docs/epics/README.md`.
- Every issue names its epic when known: first body line `**Epic:** <CODE>` plus the label `Epic-<NN>-<CODE>` (NN = line position in `config/git/epics.txt`; append, never reorder). Create labels with `tools/epic-labels.sh`.
- Use the project `.venv` (`.venv/Scripts/python`), never the global Python. Every feature ships with pytest tests in the same PR.
- Logic goes in package modules; `cli.py` and `server/app.py` stay thin and call the same functions, so dashboard and CLI numbers always agree.
- The server binds to `127.0.0.1` and has no login. Don't change the default bind address without adding auth.
- Military conversion rules must cite their source (regulation or guidance) in docs; ask before assuming any conversion rule.
- Ask before deciding anything in `docs/design/FEATURES.md` "Open questions"; they set the data format.
