---
description: Resume work — read the handoff doc, report recent PRs, suggest next steps
---

The maintainer typed `resume`. Read `AI_RESUME_HANDOFF.md` (especially "Work in progress")
and the repo instruction files (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`). Then give a
short, scannable briefing — do NOT change code until the maintainer chooses a direction:

1. **Refresh:** `git fetch --all --quiet`.
2. **Last 5 PRs created:**
   `gh pr list --state all --limit 5 --json number,title,state,createdAt` — one line each.
   **Last 5 PRs completed (merged):**
   `gh pr list --state merged --limit 5 --json number,title,mergedAt` — one line each.
   (This repo tracks work as PRs, not GitHub Issues. If Issues are ever adopted, also run
   `gh issue list --state all --limit 5`.)
3. **In flight:** `gh pr list --state open`, `git branch -r --no-merged origin/main`,
   `gh release list --limit 1`.
4. **Suggest what to work on next:** if "Work in progress" in `AI_RESUME_HANDOFF.md` has an
   unfinished task, list it FIRST as the priority; then 1–2 more from "Open issues &
   recommended next steps", each with a one-line rationale.
5. STOP and ask which direction to take. Keep it concise.
