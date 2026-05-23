---
description: Resume work — summarize the last 5 completed PRs/issues and suggest what's next
---

Help me resume work on this repository. First read `docs/ai-handoff/AI_RESUME_GUIDE.md`
for build norms, documentation approach, and project history. Then present a short,
scannable briefing (do NOT start changing code until I pick a direction):

1. **Refresh:** `git fetch --all --quiet`.

2. **Last 5 completed items** — the 5 most recently merged pull requests:
   `gh pr list --state merged --limit 5 --json number,title,mergedAt,headRefName`
   Summarize each in one line (what it delivered). Also run
   `gh issue list --state closed --limit 5` in case GitHub Issues are used (this repo has
   historically tracked work via PRs, not Issues, so merged PRs are the main "completed"
   signal).

3. **In flight / not yet shipped:**
   - open PRs: `gh pr list --state open`
   - unmerged work branches: `git branch -r --no-merged origin/main`
   - latest release: `gh release list --limit 1`
   - and note the staged work described in the guide's "Current state & next steps".

4. **Suggest what to work on next** — give me 2-4 concrete options grounded in the above
   (e.g. ship the staged `wip/wizard-ux` work as the next release via `/release`, fix the
   broken `claude-review` CI check, the restore-99%-coverage plan, etc.) and recommend one
   with a one-line rationale.

Keep the whole briefing brief and easy to scan. End by asking which direction I want.
