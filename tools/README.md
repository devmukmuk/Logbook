# Tools

Development tooling, not application code.

| Folder | Purpose |
|---|---|
| [`dev-docs/`](dev-docs/) | The ChangeIt/FinishIt/PostMerge workflow specs the assistant follows for git/GitHub work. Start with [`dev-docs/CHANGEIT.md`](dev-docs/CHANGEIT.md). |
| [`git-hooks/`](git-hooks/) | Commit-message and branch-name validation, guards against direct commits and pushes to `main`, and a guard against committing personal data (`data/`, spreadsheets, PDFs, resumes, ...). Installed per-clone via `git-hooks/install.sh`. |
| [`epic-labels.sh`](epic-labels.sh) | Creates/updates the `Epic-<NN>-<CODE>` GitHub labels from `config/git/epics.txt`. Re-run after adding an epic. |

## First-time setup for a new clone

```bash
tools/git-hooks/install.sh
```

`.git/hooks/` is not tracked, so re-run `install.sh` whenever anything in
`tools/git-hooks/` changes (the pre-commit hook calls `check-data-files.sh`,
which is copied alongside it).

Hooks that reject a commit or push can be bypassed with `--no-verify`; that is
reserved for the repo owner in an emergency.
