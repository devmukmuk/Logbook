# Design Docs

Design decisions and requirements, written before the code that implements
them. One topic per file. When a decision changes, update the doc in the same
PR as the code.

| Doc | Status | Topic |
|---|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Accepted | Stack, repository layout, data folder, server and CLI structure |
| [FEATURES.md](FEATURES.md) | Draft | Intended features per epic, open questions |
| [DATA-STORAGE.md](DATA-STORAGE.md) | Accepted | Logbooks (one or many, consolidated), file + JSON sidecar per record, rebuildable SQLite index, intake, staging, first importers |

New design docs: add a file here named for the topic (for example
`DATA-MODEL.md` or `IMPORT-FOREFLIGHT.md`), add a row to the table above, and
link it from the issue that implements it.
