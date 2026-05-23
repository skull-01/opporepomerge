---
description: Resume work — read the handoff doc, report recent PRs, suggest next steps
---

The maintainer typed `resume`. Read `AI_RESUME_HANDOFF.md` (especially "Work in progress")
and the repo instruction files (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`). Then give a
short, scannable briefing — do NOT change code until the maintainer chooses a direction:

1. **Environment preflight — make the machine ready to build/test the app BEFORE briefing.**
   The readiness checklist (requirements, why, check, fix) is `AI_RESUME_HANDOFF.md` §2. Run
   the checks below, print a small readiness table (Requirement | Status), then:
   - **All green** → one line `Environment: ready ✓` and continue.
   - **An *auto* row missing** (`.venv`, a dev dependency, or paramiko) → **install it
     automatically** (idempotent): `python -m venv .venv` (only if absent), then
     `.venv\Scripts\python.exe -m pip install -r requirements-dev.txt paramiko`; re-check and
     report what was installed.
   - **A *manual* row missing/unauthenticated** (Python ≥3.9, git, gh) → do NOT auto-install
     a system/auth change; print the exact fix command and STOP for the maintainer.
   Checks (Windows paths; on POSIX use `.venv/bin/python`):
   - `python --version` (need ≥3.9) · `git --version` · `gh auth status`
   - `.venv\Scripts\python.exe --version`
   - `.venv\Scripts\python.exe -c "import pytest, xdist, coverage, yaml, ruff, mypy, paramiko"`
2. **Refresh:** `git fetch --all --quiet`.
3. **Last 5 PRs created:**
   `gh pr list --state all --limit 5 --json number,title,state,createdAt` — one line each.
   **Last 5 PRs completed (merged):**
   `gh pr list --state merged --limit 5 --json number,title,mergedAt` — one line each.
   (This repo tracks work as PRs, not GitHub Issues. If Issues are ever adopted, also run
   `gh issue list --state all --limit 5`.)
4. **In flight:** `gh pr list --state open`, `git branch -r --no-merged origin/main`,
   `gh release list --limit 1`.
5. **Suggest what to work on next:** if "Work in progress" in `AI_RESUME_HANDOFF.md` has an
   unfinished task, list it FIRST as the priority; then 1–2 more from "Open issues &
   recommended next steps", each with a one-line rationale.
6. STOP and ask which direction to take. Keep it concise.
