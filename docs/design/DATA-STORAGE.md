# Data Storage

Status: **Proposed** (2026-11-25), issue #1. Answers [FEATURES.md](FEATURES.md#open-questions) Q1 (storage format) and Q4 (data folder location), subject to the decisions at the end.

## The problem

Logbook data arrives in many forms, and most of it is **documents**, not rows:

| Kind | Typical format | Holds |
|---|---|---|
| Military flight records | PDF (often scanned) | per-sortie or monthly flight time, crew position, aircraft |
| Civil / commercial logbooks | PDF, CSV, XLS/XLSX | per-flight entries |
| Military flight certifications | PDF | qualifications, upgrades, check rides |
| FAA certificates | PDF / scan | pilot certificates and ratings |
| Type ratings | PDF / scan | type, date, limitations |
| Medical certificates | PDF / scan | class, issue date, limitations |
| Resumes | DOCX, PDF | career summary, many versions over time |
| Work documents | PDF, DOCX, XLSX | employment records, training, letters |

Some of these become **structured data** (flights, credentials with expiry dates). All of them must stay available **as the original**, because a hiring board or the FAA (8710-1, ATP application) asks for proof, and a converted military number is only as good as the record it came from.

## Design in one paragraph

Each record is **a file plus a JSON sidecar** beside it (`<file>.meta.json`), the same pattern as DigitalArchive ([its SIDECAR.md](https://github.com/devmukmuk/DigitalArchive/blob/main/docs/SIDECAR.md)). The original file is never changed. The sidecar holds everything Logbook knows about that file: what it is, its dates, the credential it proves, the flights read from it and your corrections. A **SQLite index** is built from the sidecars for search, totals and the dashboard. It holds nothing that isn't in a sidecar, so it can be deleted and rebuilt at any time. These files, sidecars and index make up a **Logbook**: a self-contained folder, just as DigitalArchive has an *archive*. You can have several Logbooks, run tools and reports on one at a time, or **consolidate** several into one set of totals. **PDF first**: phase 1 handles PDFs only; other formats follow with the same pattern. Logbooks live **inside the VeraCrypt vault**.

## Principles

1. **Originals are evidence.** A file is copied in byte-for-byte, hashed (SHA-256), made read-only, and never edited or renamed after intake. Corrections go in the sidecar, never in the file.
2. **The sidecar is the source of truth; the index is a cache.** `logbook index --rebuild` recreates `logbook.sqlite` from the files and sidecars alone. Losing the index loses nothing.
3. **A folder that makes sense without the app.** A file and its sidecar travel together. Copy a folder out of the vault and the metadata comes with it, readable in any text editor.
4. **Provenance on every fact.** Each flight or credential lives in the sidecar of the document it came from, with a page (or row) reference, so the dashboard can open the source behind any number.
5. **Raw before converted.** Military records keep their original fields (crew position, sorties, mission symbol). Civil categories are *derived* by a named, versioned conversion rule, so a rule change can be re-run and explained.
6. **Staged extraction, your edits win.** Extracted rows start as `pending` and become `accepted` after review. Anything you set by hand (the `user` block, corrected flight fields) is never overwritten by a re-run.
7. **Encrypted at rest, plain while open.** No app-level crypto (same decision as Vault and SimplePass): the vault container is the protection.

## Logbooks: one or many

A **Logbook** is a folder holding a `logbook.yaml`; that folder is the Logbook's root, the way `da-archive.yaml` makes a DigitalArchive archive. Everything for that Logbook (documents, sidecars, index, logs) lives under its root, so it can be copied, backed up or retired as one unit.

Ways you might split them (your choice, see D7): one per career phase (`usaf`, `airline`), one per source (military records vs civil logbooks), or a single Logbook for everything. A scratch Logbook is also handy for trying an importer before running it on the real one.

**`logbook.yaml`** (small, hand-editable):

```yaml
name: usaf                    # short id used on the command line
title: USAF flying, 1998-2014
owner: <pilot name>
created: 2026-11-25
categories: [...]             # optional: override or extend the default category list
```

**Which Logbook a command works on**, first match wins (same order as DA):

1. `--logbook <name or path>` on the command line
2. `LOGBOOK_DIR` environment variable (tests point it at a temp folder)
3. the current folder, or a parent of it, that holds a `logbook.yaml`
4. otherwise: stop and list the registered Logbooks, rather than guess

**Registry:** `%LOCALAPPDATA%\Logbook\logbooks.json` lists every Logbook this computer knows (name, path, title, last used), written by `logbook new` and refreshed on every command, like DA's `archives.json`. `logbook list` shows them and whether each is reachable (a Logbook in an unmounted vault shows as not connected). A missing root is never recreated silently.

**Commands:**

| Command | Does |
|---|---|
| `logbook new <path> --name <name>` | create a Logbook folder (`logbook.yaml`, `documents/`, `inbox/`, ...) and register it |
| `logbook list` | registered Logbooks, connected or not |
| `logbook --logbook usaf <tool> ...` | run any tool on one Logbook |
| `logbook --logbooks usaf,airline <report>` / `--all` | run a read-only report on several Logbooks consolidated |
| `logbook serve` | dashboard with a Logbook picker, including "All (consolidated)" |

## Consolidation

Reports and the dashboard can read several Logbooks at once; tools that **change** data (intake, importers, review) always work on exactly one.

- Consolidation reads each Logbook's own index (SQLite `ATTACH`, read-only) and combines the rows. It never copies files or sidecars between Logbooks and never writes to them.
- Every consolidated row keeps its Logbook name, so a total can be broken down by Logbook and any number still opens its source document.
- **Duplicates across Logbooks:** the same document (same SHA-256) filed in two Logbooks counts once. Flights read from *different* documents that look like the same flight (same date, aircraft and times, for example a military record and a later civil logbook that copied it) are flagged in a "possible duplicates" list for you to settle, never dropped automatically. Your decision goes in the sidecar of the flight you exclude (`status: duplicate`, pointing at the one kept).
- A Logbook that isn't connected is reported as missing from the consolidated result, never silently left out of the totals.

## Where the data lives

Each Logbook's root goes inside the mounted vault (for example `V:\logbooks\usaf\` if the vault mounts as `V:`). The repo's `data/` folder is only a development Logbook with invented data.

```
<logbook root>/
  logbook.yaml                     marks the folder as a Logbook
  documents/                       originals + sidecars, read-only after intake
    military-records/
      2014-06-30_c17-monthly-flight-record_3fa9c2e1.pdf
      2014-06-30_c17-monthly-flight-record_3fa9c2e1.pdf.meta.json
    military-quals/
    civil-logbooks/
    faa-certificates/
    type-ratings/
    medical/
    training/
    resumes/
    employment/
    other/
  inbox/                           drop new files here; `logbook intake` files them
  exports/                         generated summaries and application breakdowns
  backups/                         sidecar snapshots before bulk changes
  logs/                            logbook.jsonl, one line per command/event
  .logbook/
    logbook.sqlite                 the index (rebuildable)
```

**Stored filename:** `<doc-date>_<slug>_<hash8>.<ext>`. The date sorts the folder in Explorer, the slug says what it is, and the first 8 hex digits of the SHA-256 make the name unique. The original filename and path are kept in the sidecar.

The current `config.py` (one `data/` folder from `LOGBOOK_DATA_DIR`, with `imports/`) is replaced by Logbook selection as above: `LOGBOOK_DATA_DIR` becomes `LOGBOOK_DIR`, `imports/` becomes `inbox/`, and `backups/` and `.logbook/` are added.

## The sidecar (schema 1)

`<file>.meta.json`, UTF-8, pretty-printed, written atomically (`.tmp` + replace). Organized in blocks like DigitalArchive's; a block is left out until it has something to say.

```json
{
  "schema":     {"name": "logbook.sidecar", "version": 1},
  "file":       {"stored_name", "original_name", "source_path", "extension", "mime",
                 "size_bytes", "pages", "sha256", "added_at"},
  "document":   {"category", "title", "doc_date", "issuer", "subject", "tags"},
  "text":       {"method": "pdf-text | ocr | mixed", "pages_with_text", "extracted_at",
                 "ssn_masked": true},
  "credential": {"kind", "authority", "name", "number", "class", "issued", "expires",
                 "limitations"},
  "flights":    {"importer", "importer_version", "conversion_rule", "read_at", "status",
                 "rows": [
                   {"id", "page", "status": "pending | accepted | rejected",
                    "date", "aircraft", "tail", "dep", "arr", "total", "pic", "sic",
                    "night", "cross_country", "actual_instrument", "sim_instrument",
                    "day_landings", "night_landings", "approaches", "remarks",
                    "military": {"service", "crew_position", "mission_symbol", "sorties",
                                 "primary", "secondary", "instructor", "evaluator"},
                    "edited": ["night"]}
                 ]},
  "user":       {"title", "doc_date", "tags", "notes"},
  "history":    [{"at", "action", "detail"}]
}
```

| Block | Written by | Notes |
|---|---|---|
| `file` | intake, once | identity of the original; `sha256` ties sidecar and file together |
| `document` | intake (suggested from the filename, confirmed by you) | what the file is |
| `text` | text extraction | facts about the text, **not the text itself**: page text lives only in the index, so the sidecar never holds an SSN or medical detail in plain text |
| `credential` | CERT epic | for certificates, ratings, medicals, military quals; `expires` drives dashboard alerts |
| `flights` | IMP/CONV importers | the flights this document holds, each with its page; `military` keeps the original fields; `edited` lists fields you corrected, which a re-run keeps |
| `user` | you | always wins over the same field in another block |
| `history` | every change | what changed, when, by which command |

Raising the schema version follows DigitalArchive's rule: bump the version, teach readers the old shape, add `logbook sidecar upgrade` that backs up and rewrites, and record the change in a versions table here.

**Flights with no document** (entered by hand later) still follow the pattern: they go in a small Logbook-generated document, for example `civil-logbooks/2026_manual-entries.json`, with its own sidecar. Every fact is still a file plus a sidecar.

## The index (SQLite)

One per Logbook: `<root>/.logbook/logbook.sqlite`, built by `logbook index` from every sidecar (incremental: a sidecar whose size and mtime are unchanged is skipped; `--rebuild` starts from empty). Never edited directly; every command that changes facts writes the sidecar first, then updates the index.

```
documents        sha256 PK, path, sidecar_path, category, title, doc_date, pages,
                 sidecar_mtime, indexed_at
document_pages   sha256, page, text            (SSN-masked)
documents_fts    FTS5 over document_pages.text  (logbook search)
credentials      sha256, kind, authority, name, number, class, issued, expires
flights          sha256, row_id, page, status, date, aircraft, tail, ...,
                 origin (civil | military), conversion_rule
aircraft         designation, make_model, category, class, engines, turbine,
                 military, civil_equivalent  (seeded from a reference table)
index_meta       schema_version, built_at
```

Why SQLite for the index: totals in the style of 14 CFR 61.159 and rolling windows over thousands of flights are one SQL query; FTS5 gives full-text search across every record; it is standard-library `sqlite3` and opens in DB Browser for SQLite, like the Vault project. Why not SQLite as the *source of truth*: a single database file is opaque outside the app and one bad write can damage everything, while a sidecar beside each file is readable, diffable and survives on its own.

## Intake

`logbook intake [FILE ... | --inbox]` (phase 1: `.pdf` only; anything else is reported and left where it is):

1. Hash the file; if that SHA-256 is already in the index (or in a sidecar in `documents/`), report the duplicate and stop.
2. Suggest the category, title and document date from the filename, and ask (or take `--category`, `--title`, `--date`).
3. Copy into `documents/<category>/<stored name>`, verify the copy's hash, make it read-only, write the sidecar (`file`, `document`, `history`), and only then remove the file from `inbox/`. A file outside `inbox/` is never moved or deleted.
4. Extract text per page: embedded PDF text first, OCR (Tesseract, already installed on Charlie, with Poppler) for pages with none. Mask SSN-shaped numbers, store page text in the index only, and record `text` facts in the sidecar.
5. Update the index and log one line to `logs/logbook.jsonl`.

Reading *structured* data (flights, credentials) is a separate per-importer step (IMP, CONV and CERT epics) run on documents already filed. It writes `pending` rows to the sidecar for review on the dashboard.

**Other formats later:** CSV and XLS/XLSX logbook exports, DOCX resumes and image scans get the same file-plus-sidecar treatment, each in its own issue. Originals stay in their own format (a spreadsheet is not converted to PDF), so nothing is lost.

## Sensitive data

- Military records and DD-214s often carry an SSN. Page text is **masked** (`***-**-1234`) before it reaches the index, and the sidecar never holds page text at all.
- Medical documents are filed like any other, but the dashboard shows only class, dates and limitations, never page text.
- Nothing personal enters the repo: the scaffold's `.gitignore` and hooks stay, and tests use invented PDFs generated in `tests/fixtures/`.
- The dashboard stays bound to `127.0.0.1`.

## Backups

- The vault already gives off-machine copies (`E:\workflows\05-VAULT.md`: dismount, copy to Texas/Dale, verify). Because the files and sidecars are the data, that procedure backs up everything Logbook has.
- Before a bulk change (`sidecar upgrade`, re-running an importer over many documents), the sidecars it touches are copied to `backups/<timestamp>-<command>/`, with a `--restore` option, as in DigitalArchive.
- The index needs no backup: rebuild it.
- `logbook` refuses to run on a Logbook whose root is missing (vault not mounted), rather than silently creating an empty one on another drive.

## Implementation order (follow-up issues)

1. **DATA**: Logbooks: `logbook.yaml`, `logbook new`, selection order (`--logbook`, `LOGBOOK_DIR`, cwd), registry + `logbook list`, refuse-if-missing, JSON-lines logging.
2. **DATA**: the `SidecarService` (load, save, update block, history, atomic write) with schema 1.
3. **DATA**: `logbook intake` for PDFs: hash, dedupe, file, read-only, sidecar.
4. **DATA**: `logbook index [--rebuild]` and the documents table; dashboard Documents page with the Logbook picker.
5. **DATA**: text extraction + OCR + SSN masking, `document_pages` + FTS5, `logbook search`.
6. **CERT**: `credential` block, entry from CLI and dashboard, expiry tiles.
7. **IMP + CONV**: first flight importer for the most important PDF record type, pending → accepted review, then the military conversion rules.
8. **DATA**: consolidation: `--logbooks` / `--all` for reports, "All" on the dashboard, cross-Logbook duplicate list.
9. **IMP**: CSV/XLS(X) logbook exports; DOCX resumes.

## Decisions needed

| # | Decision | Recommendation |
|---|---|---|
| D1 | Logbooks inside the VeraCrypt vault? Which drive letter does it mount as? | Yes; Logbook roots under `<vault>:\logbooks\` |
| D2 | Existing files: copy them in (originals stay where they are) or move them? | Copy. Retire the old copies by hand once you trust the catalog. |
| D3 | Are the ten categories right? Anything missing (simulator records, flight school records, awards)? | Start with these; `other/` catches the rest |
| D4 | Mask SSNs in the searchable text? | Yes |
| D5 | Where do the existing files live today, roughly how many, and how many are scans versus text PDFs? | Decides how much OCR work step 4 is |
| D6 | Which PDF record type should the first flight importer read (for example a specific military flight-record printout)? | The one holding the most hours |
| D7 | How to split into Logbooks: one per career phase, one per source, or one for everything? Where do non-flight documents (medical, FAA certs, resumes) go when there are several? | One per career phase, plus a `career` Logbook for certificates, medicals, resumes and work documents; consolidate for totals |
