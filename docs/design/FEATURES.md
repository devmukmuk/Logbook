# Features

Status: **Draft** (2026-11-25). This is the intended scope from the repository
description, grouped by epic. Nothing here is built yet beyond the DEV
scaffold. The open questions at the end need answers before the DATA epic
starts, because they decide the storage format.

## DATA: Logbook data model & storage

- One record per flight: date, aircraft (type and tail), route, times
  (total, PIC, SIC, dual, solo, cross-country, night, actual/simulated
  instrument, simulator), landings (day/night), approaches, remarks.
- Aircraft list with category/class, multi-engine, turbine, complex/high-performance.
- Totals and rolling windows (last 90 days, 6 months, 12 months).
- Storage: each record is the original file plus a JSON sidecar; a rebuildable SQLite index on top. See [DATA-STORAGE.md](DATA-STORAGE.md).

## IMP: Import tools

- Import from existing logbook exports into `data/`, keeping the raw file in
  `data/imports/`.
- Column mapping, duplicate detection, and `--dry-run` that reports what
  would change.

## CONV: Military conversions

- Convert military flight time to civil categories: PIC/SIC from crew
  position, cross-country, night, instrument, landings from sortie records.
- Conversion rules documented per service and per rule, with the source
  regulation or guidance cited, so every converted number can be explained.

## CERT: Certificates, ratings & medical

- Progress toward ATP (and restricted ATP) and commercial requirements under
  14 CFR 61, shown as "have / need" by category.
- Medical certificate class, issue date and expiry by class and age.
- Currency (passenger, night, instrument).

## CAR: Career support

- Airline-application style hour breakdowns (turbine, multi, PIC turbine,
  last 12 months, and so on).
- Data for the resume (totals, aircraft flown, certificates held), exported
  to `data/exports/`.

## DASH: Dashboard server

- Dashboard of totals, recent flights, and charts of hours over time and by
  aircraft.
- Pages for each epic's output (conversion report, ATP progress, application
  breakdown).

## CLI: Command-line tools

- `logbook import ...`, `logbook convert ...`, `logbook totals`,
  `logbook export ...` as the epics land.

## Open questions

| # | Question | Decides |
|---|---|---|
| Q1 | Storage format: one JSON file, CSV, or SQLite? **Proposed: file + JSON sidecar, SQLite index, PDF first, [DATA-STORAGE.md](DATA-STORAGE.md).** | DATA model and every importer |
| Q2 | Where do your existing hours live today (ForeFlight, LogTen, MyFlightbook, a spreadsheet, paper)? Which import comes first? | IMP order |
| Q3 | Which military service(s) and record types need converting (for example an Air Force ARMS or Navy NATOPS logbook printout)? | CONV rules |
| Q4 | Should the data folder default to a vault location instead of `data/` in the repo? **Proposed: yes, via `LOGBOOK_DATA_DIR`, [DATA-STORAGE.md](DATA-STORAGE.md#where-the-data-lives).** | config default |
| Q5 | Which job applications or resume formats matter most (a specific airline portal, generic resume)? | CAR outputs |
