# tools/dev-docs/CHANGEIT.md

1. **Purpose**
   <pre lang="markdown">
   ChangeIt is the standardized implementation workflow for:
   - bug fixes
   - enhancements
   - refactors
   - small feature additions

   When the user says:
   "changeit"

   the assistant should:
   - analyze the requested change
   - infer implementation scope and epic
   - generate git/github workflow commands
   - generate branch naming
   - generate issue/PR templates
   - follow project commit conventions
   </pre>

1. **Assistant Responsibilities**
   <pre lang="markdown">
   The assistant should:

   - Review current git status
   - Infer likely epic and scope (see docs/epics/README.md)
   - Suggest branch names
   - Suggest issue titles
   - Generate issue bodies
   - Put `**Epic:** <CODE>` as the first line of every issue body and apply the
     matching `Epic-<NN>-<CODE>` label (see "Epic Labels" below)
   - Generate commit messages
   - Generate PR templates
   - Generate git workflow commands
   - Prefer running tests before commit
   - Avoid runtime/generated files unless intentional
   </pre>

1. **Command Output Rules**
   <pre lang="markdown">
   When generating terminal commands:

   - ALWAYS use plain fenced markdown code blocks
   - Prefer ```bash fenced blocks
   - NEVER use writing blocks for terminal commands
   - NEVER interleave commentary inside command blocks
   - Output must be directly copy/paste safe for Git Bash
   </pre>

1. **Commit Subject Format**
   <pre lang="markdown">
   All commit subjects (first line) MUST follow:

   <type>(<epicAbbrev>): <shortDescription>

   type:             feat | fix | docs | test | refactor | perf | build | chore
   epicAbbrev:       DATA | IMP | CONV | CERT | CAR | DASH | CLI | DEV | DOC
                      (config/git/epics.txt is the source of truth;
                      docs/epics/README.md maps each code to its epic)
   shortDescription: imperative mood, verb + noun

   Examples:
   - feat(DATA): add flight entry model
   - fix(IMP): handle blank remarks column in CSV import
   - docs(DOC): describe the data folder layout

   Merge and revert commits are exempt.

   Enforced locally by tools/git-hooks/commit-msg (run tools/git-hooks/install.sh
   once per clone -- .git/hooks/ isn't tracked by git). Branch names are enforced
   the same way by tools/git-hooks/pre-push.

   Branch name format:

   <type>/<issue>-<EPIC>-<short-description>
   Example: feat/12-DATA-add-flight-entry-model

   Direct commits to main are blocked by tools/git-hooks/commit-msg and pushes
   to main are blocked by tools/git-hooks/pre-push. Every change goes through
   issue -> branch -> pull request.
   </pre>

1. **Canonical Workflow Template**
   <pre lang="bash">
   BRANCH=""
   ISSUE_TITLE=""
   ISSUE_BODY=""
   EPIC_LABEL=""
   COMMIT_MESSAGE=""

   ISSUE_URL=$(gh issue create \
     --title "$ISSUE_TITLE" \
     --body "$ISSUE_BODY" \
     --label "$EPIC_LABEL")

   ISSUE_NUMBER=$(basename "$ISSUE_URL")

   git checkout main
   git pull origin main
   git checkout -b "$BRANCH"

   git add .

   git status

   if [ -x ".venv/Scripts/python" ]; then
      .venv/Scripts/python -m pytest -q || [ $? -eq 5 ] || exit 1
   else
      echo "No .venv found. Skipping automated tests."
   fi

   git commit -m "$COMMIT_MESSAGE"

   git push -u origin "$BRANCH"

   gh pr create \
     --base main \
     --head "$BRANCH" \
     --title "$ISSUE_TITLE" \
     --body "
   ## Summary
   - ...

   Closes #$ISSUE_NUMBER
   "
   </pre>

1. **Epic Labels**
   <pre lang="markdown">
   When the epic is known, every issue:
   - starts its body with: **Epic:** <CODE>   (e.g. **Epic:** DATA)
   - carries the label Epic-<NN>-<CODE>       (e.g. Epic-01-DATA, Epic-02-VAL)

   EPIC_LABEL in the template above holds that label.

   If the epic is NOT known yet, drop the "Epic:" line and the --label line
   from the template, and add both once the epic is decided.

   The number NN is the code's line position in config/git/epics.txt (see
   docs/epics/README.md). Run tools/epic-labels.sh after adding an epic to
   create its GitHub label. Use tools/epic-labels.sh --list to print the names.
   </pre>

1. **Test Runner**
   <pre lang="markdown">
   Tests run with pytest from the project's own .venv (never the global Python).

   pytest exits with code 5 when it collects no tests. The template treats that
   as a pass so the workflow works before the first test exists; once tests
   exist, any failure stops the workflow.

   Every new feature ships with its unit tests in tests/ in the same PR.
   </pre>

1. **Post Merge Cleanup**
   <pre lang="bash">
   After the PR is merged, use POSTMERGE.md.
   </pre>

1. **Workflow Preferences**
   <pre lang="markdown">
   Prefer:
   - small incremental phases
   - PR-friendly changes
   - test-first validation
   - minimal-risk implementation steps

   Avoid:
   - large multi-feature commits
   - direct commits/pushes to main
   - mixing refactors with unrelated fixes
   - committing generated runtime files
   </pre>

<br>Author: Mike Mattinson/Chat
<br>Updated: Nov/25/2026
