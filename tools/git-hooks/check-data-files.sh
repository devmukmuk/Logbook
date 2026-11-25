#!/bin/sh
# Refuses paths that look like personal Logbook data. Reads paths from standard input, one per line
# (as printed by `git diff --cached --name-only` or `git ls-files`), prints each offender and why to
# standard error, and exits 1 if there was any. Exits 0 if every path is fine (or there were none).
#
# Used by the pre-commit hook on the staged files, and by tests/test_check_data_files.py on every
# tracked file (a backstop, because hooks are local and can be bypassed).
#
# This repository is PUBLIC. Refused:
#   * anything under data/, imports/, exports/ or logs/ at the top of the repository
#   * spreadsheets and documents (.csv .tsv .xls .xlsx .xlsm .ods .docx .doc .pdf) anywhere,
#     because a logbook export, medical certificate or resume is exactly that kind of file
#   * .env files (except .env.example)
# Allowed regardless: everything under tests/fixtures/ and logbook/templates/ (invented sample
# data, meant to be tracked) and docs/ (deliberate, reviewed documentation).
# Names are compared without regard to case, because Windows treats Data/ as data/.

found=0

while IFS= read -r path; do
    # Drop a trailing CR (input piped from Windows tools), or *.csv would never match "x.csv<CR>".
    path=$(printf '%s' "$path" | tr -d '\r')
    [ -n "$path" ] || continue
    lower=$(printf '%s' "$path" | tr 'A-Z' 'a-z')

    case "$lower" in
        tests/fixtures/*|logbook/templates/*|docs/*) continue ;;
    esac

    reason=""
    case "$lower" in
        data/*)    reason="the live logbook data folder" ;;
        imports/*) reason="raw import files from other logbooks" ;;
        exports/*) reason="generated exports of your logbook" ;;
        logs/*)    reason="a log; it may name flights, people or employers" ;;
    esac
    if [ -z "$reason" ]; then
        case "${lower##*/}" in
            .env.example) ;;
            .env|.env.*) reason="environment settings; may hold keys" ;;
            *.csv|*.tsv|*.xls|*.xlsx|*.xlsm|*.ods)
                reason="a spreadsheet; it may be a real logbook export" ;;
            *.doc|*.docx|*.pdf)
                reason="a document; it may be a resume, certificate or medical" ;;
        esac
    fi

    if [ -n "$reason" ]; then
        if [ "$found" -eq 0 ]; then
            echo "ERROR: refusing to commit files that look like personal Logbook data:" >&2
            echo "" >&2
        fi
        found=$((found + 1))
        printf '  %s   (%s)\n' "$path" "$reason" >&2
    fi
done

if [ "$found" -gt 0 ]; then
    echo "" >&2
    echo "This repository is public. Real logbook, medical, certificate and resume data must" >&2
    echo "never enter git. Invented samples belong in tests/fixtures/ or logbook/templates/." >&2
    echo "" >&2
    echo "  Unstage a file:   git restore --staged <file>" >&2
    echo "  Keep it out:      check that .gitignore covers it" >&2
    echo "  Already committed? Removing it is always allowed:  git rm --cached <file>" >&2
    echo "" >&2
    echo "Emergency bypass (repository owner only): git commit --no-verify" >&2
    exit 1
fi

exit 0
