---
description: Resume work — read the handoff doc, report addon + configurator activity, suggest next steps per area
---

The operator typed `resume`. Authoritative spec is `AI_RESUME_HANDOFF.md` §1; this file is
the runnable checklist. Read the handoff (especially **§3a Addon WIP** and **§3b
Configurator WIP**) and the repo instruction files (`AGENTS.md`, `CLAUDE.md`,
`CONTRIBUTING.md`). Then give a short, scannable briefing — do NOT change code until the
operator picks **one area and one theme**:

1. **Environment preflight for BOTH areas — run §2a of the handoff.** Print a small
   readiness table (`Row | Prereq | Status | Tier`). The single Windows env serves both
   areas; install anything missing per its tier:

   - **`auto-repo`** missing (`.venv`, dev deps, `node_modules`, area labels, icon stub) →
     install idempotently, re-check, report. Concretely:
     - `python -m venv .venv` (if absent), then
       `.venv\Scripts\python.exe -m pip install -r requirements-dev.txt paramiko`
     - `cd configurator; npm install` (if `configurator\node_modules` absent), then `cd ..`
     - `gh label create area:addon --color 0E8A16 --description "Kodi add-on (Python)" --force`
     - `gh label create area:configurator --color 5319E7 --description "Windows configurator (Tauri 2)" --force`
   - **`auto-system`** missing (git, Python, Node, Rust, MSVC Build Tools, WebView2) →
     attempt `winget install --id <pkg> -e --silent --accept-source-agreements
     --accept-package-agreements` (PowerShell). On success, re-check and continue. On
     failure (no winget, package needs admin, network), print the manual fix from §2a
     and **STOP**.
   - **`manual`** missing (`gh auth status` failed, etc.) → print the exact fix and STOP.

   All green → one line `Environment: ready ✓ (addon + configurator)` and continue.

2. **Refresh state.** `git fetch --all --quiet`.

3. **Report recent activity per area — two parallel blocks.**

   **Addon area:**
   - *Last 5 issues created:* `gh issue list --label area:addon --limit 5 --state all --sort created --json number,title,state,createdAt` — one line each as `#N <title snippet>`.
   - *Last 5 issues closed:* `gh issue list --label area:addon --limit 5 --state closed --sort updated --json number,title,closedAt` — same formatting.
   - *Work in progress:* paraphrase §3a in 2–4 lines (in-flight branch/PR, what's done, what's left, blockers).

   **Configurator area:**
   - *Last 5 issues created:* `gh issue list --label area:configurator --limit 5 --state all --sort created --json number,title,state,createdAt`.
   - *Last 5 issues closed:* `gh issue list --label area:configurator --limit 5 --state closed --sort updated --json number,title,closedAt`.
   - *Work in progress:* paraphrase §3b in 2–4 lines.

   **Unclassified tail** (≤5 rows): any open issues without either `area:` label, so they
   can be triaged. Skip the header if empty.

   *(Optional reference signals for both areas:* `gh pr list --state open`,
   `git branch -r --no-merged origin/main`, `gh release list --limit 1` — include only if
   directly relevant to a WIP entry. Don't bloat the briefing.*)

4. **Suggest themes per area, separately** (still one theme = one session per the
   handoff's §4 session-shape rule):

   - **Addon — 1–3 candidate themes**, each one line with a one-line rationale. Lead with
     any unfinished §3a entry.
   - **Configurator — 1–3 candidate themes**, each one line with a one-line rationale.
     Lead with any unfinished §3b entry.

5. **STOP and ask the operator to pick one area and one theme.** Do not start work in
   both areas in the same session.
