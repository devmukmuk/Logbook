# Data Storage

Status: **Accepted** (2026-11-25), issues #1 and #3. Answers [FEATURES.md](FEATURES.md#open-questions) Q1 (storage format), Q2 (first imports), Q3 (military records) and Q4 (data location). Decisions are recorded at the end.

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

Each record is **a file plus a JSON sidecar** beside it (`<file>.meta.json`), the same pattern as DigitalArchive ([its SIDECAR.md](https://github.com/devmukmuk/DigitalArchive/blob/main/docs/SIDECAR.md)). The original file is never changed. The sidecar holds everything Logbook knows about that file: what it is, its dates, the credential it proves, the flights read from it and your corrections. A **SQLite index** is built from the sidecars for search, totals and the dashboard. It holds nothing that isn't in a sidecar, so it can be deleted and rebuilt at any time. These files, sidecars and index make up a **Logbook**: a self-contained folder, just as DigitalArchive has an *archive*. You can have several Logbooks, run tools and reports on one at a time, or **consolidate** several into one set of totals. **PDF first**: phase 1 handles PDFs only; other formats follow with the same pattern. Logbooks live, **unencrypted**, under the project's git-ignored **`data/`** folder.

## Principles

1. **Originals are evidence.** A file is copied in byte-for-byte, hashed (SHA-256), made read-only, and never edited or renamed after intake. Corrections go in the sidecar, never in the file.
2. **The sidecar is the source of truth; the index is a cache.** `logbook index --rebuild` recreates `logbook.sqlite` from the files and sidecars alone. Losing the index loses nothing.
3. **A folder that makes sense without the app.** A file and its sidecar travel together. Copy a Logbook folder anywhere and the metadata comes with it, readable in any text editor.
4. **Provenance on every fact.** Each flight or credential lives in the sidecar of the document it came from, with a page (or row) reference, so the dashboard can open the source behind any number.
5. **Raw before converted.** Military records keep their original fields (crew position, sorties, mission symbol). Civil categories are *derived* by a named, versioned conversion rule, so a rule change can be re-run and explained.
6. **Staged extraction, your edits win.** Extracted rows start as `pending` and become `accepted` after review. Anything you set by hand (the `user` block, corrected flight fields) is never overwritten by a re-run.
7. **Plain files, kept out of git.** No encryption (decision D1). The protection is that `data/` is git-ignored, the pre-commit hook refuses data files, and a test checks every tracked file, because the repository is public.

## Logbooks: one or many

A **Logbook** is a folder holding a `logbook.yaml`; that folder is the Logbook's root, the way `da-archive.yaml` makes a DigitalArchive archive. Everything for that Logbook (documents, sidecars, index, logs) lives under its root, so it can be copied, backed up or retired as one unit.

**Split (D7): one Logbook per career phase and/or aircraft type**, for example `usaf-c17`, `usaf-t38`, `airline-b737`. Certificates, medicals, type ratings, resumes and work documents that belong to no single phase go in a `career` Logbook. A scratch Logbook is handy for trying an importer before running it on a real one. The consolidated summary across all of them is the main career view (see [Consolidation](#consolidation)).

**`logbook.yaml`** (small, hand-editable):

```yaml
name: usaf-c17                # short id used on the command line
title: USAF C-17 flying
phase: military               # military | civil | career
aircraft: [C-17A]             # aircraft types this Logbook covers (may be several)
owner: <pilot name>
created: 2026-11-25
categories: [...]             # optional: override or extend the default category list
```

**Which Logbook a command works on**, first match wins (same order as DA):

1. `--logbook <name or path>` on the command line (a bare name means `data/<name>/`)
2. `LOGBOOK_DIR` environment variable (tests point it at a temp folder)
3. the current folder, or a parent of it, that holds a `logbook.yaml`
4. otherwise: stop and list the Logbooks found, rather than guess

**Finding Logbooks:** every folder under `data/` holding a `logbook.yaml` is a Logbook; `logbook list` shows them. A Logbook somewhere else (for example on a USB drive) can be added to `%LOCALAPPDATA%\Logbook\logbooks.json` with `logbook new` or `logbook list --add <path>`, and shows as not connected when that drive is absent. A missing root is never recreated silently.

**Commands:**

| Command | Does |
|---|---|
| `logbook new <name> [--path <folder>]` | create a Logbook folder (`data/<name>/` by default) with `logbook.yaml`, `documents/`, `inbox/`, ... |
| `logbook list` | Logbooks under `data/` plus registered ones elsewhere, connected or not |
| `logbook --logbook usaf-c17 <tool> ...` | run any tool on one Logbook |
| `logbook --logbooks usaf-c17,airline-b737 <report>` / `--all` | run a read-only report on several Logbooks consolidated |
| `logbook serve` | dashboard with a Logbook picker, including "All (consolidated)" |

## Consolidation

Reports and the dashboard can read several Logbooks at once; tools that **change** data (intake, importers, review) always work on exactly one.

- Consolidation reads each Logbook's own index (SQLite `ATTACH`, read-only) and combines the rows. It never copies files or sidecars between Logbooks and never writes to them.
- Every consolidated row keeps its Logbook name, so a total can be broken down by Logbook and any number still opens its source document.
- **Duplicates across Logbooks:** the same document (same SHA-256) filed in two Logbooks counts once. Flights read from *different* documents that look like the same flight (same date, aircraft and times, for example a military record and a later civil logbook that copied it) are flagged in a "possible duplicates" list for you to settle, never dropped automatically. Your decision goes in the sidecar of the flight you exclude (`status: duplicate`, pointing at the one kept).
- A Logbook that isn't connected is reported as missing from the consolidated result, never silently left out of the totals.
- **The career summary** (`logbook summary --all`, and the dashboard's "All" view) is the main consolidated report: totals by Logbook, by aircraft type, by civil category (PIC, SIC, night, instrument, cross-country, multi-engine, turbine) and by year, with military time shown both as recorded and as converted.

## Where the data lives

Logbooks live **unencrypted** under the project folder's **`data/`** (D1), which git ignores:

```
E:\dev\repos\github.com\devmukmuk\Logbook\
  data\
    usaf-c17\          one Logbook
    airline-b737\      another
    career\            certificates, medicals, resumes, work documents
```

Tests never use `data/`: they point `LOGBOOK_DIR` at a temporary folder with invented documents.

Each Logbook's layout:

```
<logbook root>/
  logbook.yaml                     marks the folder as a Logbook
  documents/                       originals + sidecars, read-only after intake
    military-records/              AFTO Form 781s
      2009-03-14_afto-781_3fa9c2e1.pdf
      2009-03-14_afto-781_3fa9c2e1.pdf.meta.json
    military-summaries/            military flying-time summaries
    military-quals/
    airline-schedules/             monthly pilot schedules from the company
    airline-summaries/             monthly flying summaries from the company
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
  "totals":     {"importer", "importer_version", "conversion_rule", "read_at", "status",
                 "periods": [
                   {"id", "page", "status": "pending | accepted | rejected",
                    "from", "to", "aircraft", "total", "pic", "sic", "night",
                    "actual_instrument", "sim_instrument", "landings", "sorties",
                    "military": {...}, "edited": []}
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
| `totals` | IMP/CONV importers | period totals from a flying summary (a month, a year, career to date), per aircraft; see [Flights and period totals](#flights-and-period-totals) |
| `user` | you | always wins over the same field in another block |
| `history` | every change | what changed, when, by which command |

Raising the schema version follows DigitalArchive's rule: bump the version, teach readers the old shape, add `logbook sidecar upgrade` that backs up and rewrites, and record the change in a versions table here.

## Flights and period totals

The records hold time at two levels:

| Level | Comes from | Block |
|---|---|---|
| **Flight** (one sortie or leg) | AFTO Form 781s; airline monthly schedules | `flights` |
| **Period total** (a month, a year, career to date) | military flying summaries; airline monthly flying summaries | `totals` |

Both are kept, and neither is thrown away in favor of the other. The rule for reports, per Logbook, aircraft and period:

1. Where accepted flights cover the period, totals are the **sum of the flights**.
2. Where they don't, the accepted **period totals** fill the gap, so a career total is available before every 781 is read.
3. Where both exist, they are shown side by side as a **cross-check**, and a difference above a small tolerance is flagged for review (a missed 781, an OCR misread, a summary that counts differently).

Each report says which level each number came from.

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
period_totals    sha256, period_id, page, status, from, to, aircraft, total, pic, ...,
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

## First importers (D6)

The records on hand:

| Record | Form | Level | Reading it |
|---|---|---|---|
| Airline monthly flying summaries | company PDF, 5 years | period totals | text layer (expected), one fixed company layout |
| Airline monthly pilot schedules | company PDF, 5 years | flights (legs) | text layer (expected), one fixed company layout |
| Military flying summaries | scanned PDF | period totals | OCR, form layout |
| AFTO Form 781s | scanned PDF | flights (sorties) | OCR, form layout, handwriting likely in places |

Order, easiest and most valuable first:

1. **Airline monthly flying summaries → `totals`.** Text, one layout: five years of airline totals quickly.
2. **Airline monthly schedules → `flights`.** Same source, leg-level detail, cross-checked against step 1 month by month.
3. **Military flying summaries → `totals`.** OCR, but few pages and fixed fields: military career totals without reading every 781.
4. **AFTO Form 781s → `flights`.** The hardest (OCR on scanned forms, often handwritten); sortie detail cross-checked against step 3, then the **CONV** rules turn crew-position time into civil PIC/SIC.

"Expected" above is checked by the survey (next section) before any importer is written. If the airline PDFs turn out to be scans too, the order still holds, but steps 1–2 also need OCR.

## Staging: E:\logbooks (D5)

Source files are being copied to `E:\logbooks`. That folder is a **staging area**, not a Logbook: files are sorted there into intake-ready groups, then `logbook intake` copies each group into the right Logbook. `E:\logbooks` stays as the untouched source until the Logbooks are trusted. (The `E:\` drive repo ignores everything under it except `.md` files.)

Target layout, one folder per future Logbook, one subfolder per record kind:

```
E:\logbooks\
  _incoming\                 everything as copied; never edited, only copied from
  usaf-<type>\               one per military aircraft type (Logbook name)
    afto-781\
    summaries\
    quals\                   Form 8s, upgrade and check-ride records
  airline-<type>\            one per airline aircraft type
    schedules\               2021-01_schedule.pdf ...
    summaries\               2021-01_summary.pdf ...
  career\
    faa-certificates\  type-ratings\  medical\  resumes\  employment\  training\
  _duplicates\               exact copies (same SHA-256) found by the survey
  _unsorted\                 not identified yet
```

**Filenames in staging:** `YYYY-MM[-DD]_<kind>[_<aircraft>].pdf`, such as `2021-03_summary.pdf` or `2009-03-14_afto-781_c17.pdf`, so intake can read the date and kind without asking. Multi-month scans keep the first date and get a note.

**Getting there:** a read-only `logbook survey <folder>` reports, for each file: size, SHA-256, page count, whether each page has a text layer or is a scan (Poppler `pdffonts`/`pdftotext`), dates found in the filename or text, a suggested group and name, and exact duplicates. It writes a plan CSV you can edit; `logbook survey --apply <plan.csv>` then **copies** files from `_incoming` into the staging layout with the new names. Nothing is moved or deleted.

## Sensitive data

- The data is **not encrypted** (D1): anyone with access to this PC's `E:` drive can read it. Keep that in mind before syncing `data/` to a cloud folder or a shared drive.
- Military records and DD-214s often carry an SSN. Page text is **masked** (`***-**-1234`) before it reaches the index, and the sidecar never holds page text at all.
- Medical documents are filed like any other, but the dashboard shows only class, dates and limitations, never page text.
- Nothing personal enters the repo: the scaffold's `.gitignore` and hooks stay, and tests use invented PDFs generated in `tests/fixtures/`.
- The dashboard stays bound to `127.0.0.1`.

## Backups

- The files and sidecars are the data, so copying `data/` copies everything Logbook has. `E:\dev\repos\` is outside the drive-root repo and its documented backups (`E:\workflows\02-BACKUP-ARCHIVE-LIBRARY.md`), so add `data/` to that snapshot routine (a `robocopy` of `data\` into `E:\backup\logbook\<date>\` and onto Texas).
- Before a bulk change (`sidecar upgrade`, re-running an importer over many documents), the sidecars it touches are copied to `backups/<timestamp>-<command>/`, with a `--restore` option, as in DigitalArchive.
- The index needs no backup: rebuild it.
- `logbook` refuses to run on a Logbook whose root is missing (for example a registered Logbook on an unplugged drive), rather than silently creating an empty one.

## Implementation order (follow-up issues)

1. **IMP**: `logbook survey` (read-only inventory + plan CSV) and `survey --apply` (copy into the staging layout). First, because it sorts `E:\logbooks` and confirms which PDFs are scans.
2. **DATA**: Logbooks: `logbook.yaml`, `logbook new`, selection order (`--logbook`, `LOGBOOK_DIR`, cwd), `logbook list`, refuse-if-missing, JSON-lines logging.
3. **DATA**: the `SidecarService` (load, save, update block, history, atomic write) with schema 1.
4. **DATA**: `logbook intake` for PDFs: hash, dedupe, file, read-only, sidecar.
5. **DATA**: `logbook index [--rebuild]` and the documents table; dashboard Documents page with the Logbook picker.
6. **DATA**: text extraction + OCR + SSN masking, `document_pages` + FTS5, `logbook search`.
7. **IMP**: airline monthly flying summaries → `totals`; review page; first consolidated summary.
8. **IMP**: airline monthly schedules → `flights`, cross-checked against step 7.
9. **IMP + CONV**: military flying summaries → `totals`, then AFTO Form 781s → `flights`, then the military-to-civil conversion rules.
10. **DATA**: full consolidation: `--logbooks` / `--all`, "All" on the dashboard, cross-Logbook duplicate list.
11. **CERT**: `credential` block, entry from CLI and dashboard, expiry tiles.
12. **IMP**: CSV/XLS(X) logbook exports; DOCX resumes.

## Decisions

| # | Decision | Answer |
|---|---|---|
| D1 | Where do Logbooks live; encrypted? | **Unencrypted, under the project's git-ignored `data/` folder** (2026-11-25) |
| D2 | Copy existing files in, or move them? | **Copy.** `E:\logbooks` stays as the source; retire it by hand once the Logbooks are trusted |
| D3 | Are the categories right? | Default list above (with the military/airline record folders added); change any time in `logbook.yaml` |
| D4 | Mask SSNs in the searchable text? | Yes (default) |
| D5 | Where are the existing files? | **Being copied to `E:\logbooks`**; sorted there by `logbook survey` into intake-ready groups (see [Staging](#staging-elogbooks-d5)) |
| D6 | Which records come first? | **AFTO Form 781s and military flying summaries (scanned PDF); 5 years of airline monthly schedules and flying summaries (company PDF).** Order in [First importers](#first-importers-d6) |
| D7 | How to split Logbooks? | **By career phase and/or aircraft type**, plus a `career` Logbook, with a consolidated summary across all |
