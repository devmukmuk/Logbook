#!/bin/sh
# Installs this project's shared git hooks into this clone's .git/hooks/.
# Re-run after cloning or if tools/git-hooks/* changes -- .git/hooks/ isn't
# tracked by git, so it doesn't update itself.

set -e
repo_root=$(git rev-parse --show-toplevel)

# check-data-files.sh is a helper the pre-commit hook calls; it is copied so the hook works on its own.
for hook in commit-msg pre-commit pre-push check-data-files.sh; do
    cp "$repo_root/tools/git-hooks/$hook" "$repo_root/.git/hooks/$hook"
    chmod +x "$repo_root/.git/hooks/$hook"
    echo "Installed $hook into .git/hooks/."
done
