#!/bin/sh
# Creates (or updates) one GitHub label per epic: Epic-<NN>-<CODE>, e.g. Epic-01-DATA.
#
# Source of truth: config/git/epics.txt. The line position is the number, so
# append new epics at the end. The label description is the epic name from the
# table in docs/epics/README.md. Safe to re-run (uses --force to update).
#
# Requires an authenticated GitHub CLI (gh auth status).
#
# Usage:
#   tools/epic-labels.sh            create/update the labels
#   tools/epic-labels.sh --list     print the label names only, change nothing

set -e
repo_root=$(git rev-parse --show-toplevel)
epic_file="$repo_root/config/git/epics.txt"
readme="$repo_root/docs/epics/README.md"

# Colour cycle, one per epic in order.
colors="1D76DB 0E8A16 B60205 5319E7 FBCA04 D93F0B C2E0C6 6E7781 0075CA"

n=0
for code in $(grep -v '^#' "$epic_file" | grep -v '^$'); do
    n=$((n + 1))
    name=$(printf 'Epic-%02d-%s' "$n" "$code")

    if [ "$1" = "--list" ]; then
        echo "$name"
        continue
    fi

    color=$(echo "$colors" | cut -d' ' -f"$n")
    [ -n "$color" ] || color="C5DEF5"

    # Epic name from the README table row: | `Epic-NN-CODE` | CODE | Epic name | ... |
    desc=$(awk -F'|' -v c="$code" '
        { gsub(/^ +| +$/, "", $3) }
        $3 == c { gsub(/^ +| +$/, "", $4); print $4; exit }
    ' "$readme")
    [ -n "$desc" ] || desc="Epic $code"

    gh label create "$name" --color "$color" --description "$desc" --force
done
