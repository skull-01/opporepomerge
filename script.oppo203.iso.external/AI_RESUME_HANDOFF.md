# AI_RESUME_HANDOFF.md — session continuity for `script.oppo203.iso.external`

**Audience:** any AI agent (Claude, Cursor, Codex, …) starting or resuming work on this
repo. Read this file **first**. Treat live code + `git`/`gh` output as authoritative; this
file is the map and the memory.

**Repo:** `github.com/skull-01/script.oppo203.iso.external` · **Default branch:** `main`
**Last sync:** commit `394f9fc` (origin/main, 2026-05-29 — Merge PR #30 configurator scaffold) · **Tests on `main`:** 987 passed, 3 skipped (`pytest -n auto`, ~11s)
**Latest release:** v2.9.13 · **Issue model:** **hybrid** — GitHub Issues for bug/enhancement
tracking, PRs for delivery; every issue tagged `area:addon` or `area:configurator`.

**What this is:** A Python 3.9+ Kodi add-on (`script.oppo203.iso.external`) for OPPO 203/205
and compatible-clone external-player handoff, plus a new Tauri 2 + React/TS Windows
**configurator** under [`configurator/`](configurator/) that sets the add-on up (writes
`playercorefactory.xml` + the remote-bridge keymap, probes the TV/player, captures HDMI
inputs).

**Deep-archive companion** (historical builds, not the spine):
[`docs/ai-handoff/AI_RESUME_GUIDE.md`](docs/ai-handoff/AI_RESUME_GUIDE.md) and the
`Combined_AI_Handoff_*` build-reconstruction files.

---

# §1 The `resume` command

Work in this repo is split into **two areas** that share one machine and one git history:

- **Addon** — the Kodi add-on (Python under `resources/`, entry points `default.py` /
  `service.py`, release tooling under `tools/`, tests under `tests/`).
- **Configurator** — the Windows configurator app (Tauri 2 + React/TS under
  `configurator/`).

Issues are tagged with **`area:addon`** or **`area:configurator`** labels so the resume
command can summarize each area independently. Both areas live on `main`; one environment
serves both (see §2a).

When the operator types **`resume`** (alone), do exactly this:

1. **Read this file** (especially §3a "Addon work in progress" and §3b "Configurator work
   in progress") and the repo instruction files
   ([`AGENTS.md`](AGENTS.md), [`CLAUDE.md`](CLAUDE.md), [`CONTRIBUTING.md`](CONTRIBUTING.md)).
2. **Run the unified environment readiness check** in §2a — it covers prerequisites for
   **both** areas (Python venv + dev deps for addon; Node + Rust + Tauri + WebView2 for
   configurator; plus the `area:addon` / `area:configurator` GitHub labels). Print a small
   readiness table.
   - All rows green → one line `Environment: ready ✓ (addon + configurator)` and continue.
   - An *auto-repo* row missing → install it (idempotent: `venv`, `pip install`, `npm
     install`, `gh label create --force`), re-check, report what was installed.
   - An *auto-system* row missing → attempt `winget install ... --silent
     --accept-source-agreements --accept-package-agreements` (per row), re-check; on
     success continue, on failure print the manual fix and **STOP**.
   - A *manual* row missing → print the exact fix command and **STOP**.
3. **Report recent backlog activity per area.** Two parallel blocks, **Addon** then
   **Configurator**, each with:
   - *Last 5 issues created* — `gh issue list --label area:<area> --limit 5 --state all
     --sort created` — one line each as `#N <short title snippet>` (operator's "list
     issues with titles" norm).
   - *Last 5 issues closed* — `gh issue list --label area:<area> --limit 5 --state closed
     --sort updated` — same formatting.
   - *Work in progress* — paraphrase §3a (for addon) or §3b (for configurator) in 2–4
     lines: the in-flight branch/PR, what's done, what's left, blockers.

   If any issues exist that carry neither `area:addon` nor `area:configurator`, list them
   under a short **Unclassified** tail (≤5 rows) so they can be triaged.
4. **Suggest themes per area, separately** (still one theme = one session per §4).
   - **Addon — 1–3 candidate themes**, each one line, leading with any unfinished §3a
     entry.
   - **Configurator — 1–3 candidate themes**, each one line, leading with any unfinished
     §3b entry.

   **STOP and wait** for the operator to pick **one area and one theme** before doing any
   new work. Do not start work in both areas in the same session (§4 session-shape rule).

## Other natural-language triggers any agent must honor

| Trigger | Behavior |
|---|---|
| **`done for the day`** | Run §2 fully. |
| **`confirmation queue`** | List open issues whose implementing SHA was commented (per §17a / the "only operator closes" norm) but which the operator hasn't verified/closed yet. |
| **`bugs`** | `gh issue list --label type:bug --state open` — format each row as `#N <title snippet>`. |
| **`enhancements`** | `gh issue list --search "ENH- in:title" --state open` — same formatting. |
| **`backlog audit`** | Report from §17a cache first; ask before re-scanning live GitHub state (per operator norm #10). |
| **`build plan`** | Show contents of [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) (create as stub on first use). |
| **`refresh the build plan`** | Regenerate `docs/BUILD_PLAN.md` from live open issues. |
| **`dev note: <text>`** | Append `<text>` VERBATIM (dated, no editing, no summarizing) to §20. |
| **`update AI_RESUME_HANDOFF.md`** | Run the maintenance recipe at the end of §2. |

Slash-command equivalents: `/resume`, `/done-for-the-day`, `/release`.

---

# §2 The `done for the day` command

When the operator types **`done for the day`**, do exactly this:

1. **Push ALL current work to the active branch.** No work left only on this machine.
   - Tests green → normal commit + `git push -u origin <branch>`.
   - Tests red or work mid-flight → `wip: <short summary>` checkpoint commit + push. Note
     the wip status in §3 so next session knows it's not done.
2. **Update §3 "Work in progress" — overwrite §3a and §3b independently.** Touch only the
   area(s) you actually worked in this session. For each touched area: current state,
   what's in flight, the clean stopping point for tomorrow, any blockers. If you didn't
   touch an area, leave its subsection unchanged. If an area ended clean, write `(none)`
   in its subsection so next `resume` reports it as a fresh slate.
3. **Append a dated entry to §19** "Updates to this document" — one bullet per material
   change (this entry, plus anything new added during the session).
4. **Refresh the §17a backlog audit cache** if any issues were opened, closed, or
   meaningfully retitled this session.
5. **Commit + push the handoff** — `docs: end-of-day handoff <YYYY-MM-DD>` on `main` if
   you have direct-to-main rights for docs-only changes, otherwise via short-lived PR.
6. **End-of-day summary** — 2-4 lines: what shipped today, what's open, what to pick up
   first tomorrow. Do **NOT** start new feature work.

Maintenance recipe (for `update AI_RESUME_HANDOFF.md`): refresh §3, §17a; append §19; if
substantive Q&A happened, append §21; verify §2a still matches the actual readiness check.

---

# §2a Environment readiness

The readiness check verifies the **single Windows machine** can edit, test, and build
**both** areas — the Kodi add-on (Python) **and** the Tauri 2 configurator (Node + Rust +
WebView2). One pass covers both.

**Tiers.** `auto-repo` = idempotent and runs in user scope, the resume command does it
without prompting. `auto-system` = the resume command attempts `winget install` (best
effort, no admin elevation requested; user-scope installs don't need it); on success it
re-checks and continues, on failure it prints the manual fix and **STOPS**. `manual` = an
operator action the resume command will not perform (auth flows, browser-redirect installs).

| Row | Prereq | How to check (PowerShell) | Tier | Install command |
|---|---|---|---|---|
| 1 | **git** ≥ 2.30 | `git --version` | auto-system | `winget install --id Git.Git -e --silent --accept-source-agreements --accept-package-agreements` |
| 2 | **`gh` CLI** authenticated | `gh auth status` | manual | `gh auth login` (operator approves the browser flow) |
| 3 | **Python** 3.9+ on PATH | `python --version` | auto-system | `winget install --id Python.Python.3.12 -e --silent --accept-source-agreements --accept-package-agreements` |
| 4 | Repo **`.venv`** | `Test-Path .venv` | auto-repo | `cd C:\Users\rigel\Documents\gitrepo\script.oppo203.iso.external; python -m venv .venv` |
| 5 | **Python dev deps** | `.venv\Scripts\python.exe -m pytest --version` | auto-repo | `cd C:\Users\rigel\Documents\gitrepo\script.oppo203.iso.external; .venv\Scripts\python.exe -m pip install -r requirements-dev.txt paramiko` |
| 6 | **paramiko** (SSH probes) | `.venv\Scripts\python.exe -c "import paramiko"` | auto-repo | covered by row 5 |
| 7 | **Node** 20+ | `node -v` | auto-system | `winget install --id OpenJS.NodeJS.LTS -e --silent --accept-source-agreements --accept-package-agreements` |
| 8 | **npm** 10+ | `npm -v` | bundled | comes with Node row 7 |
| 9 | configurator **`node_modules`** | `Test-Path configurator\node_modules` | auto-repo | `cd C:\Users\rigel\Documents\gitrepo\script.oppo203.iso.external\configurator; npm install` |
| 10 | **Rust toolchain** 1.77+ | `cargo --version; rustc --version` | auto-system | `winget install --id Rustlang.Rustup -e --silent --accept-source-agreements --accept-package-agreements; rustup default stable` |
| 11 | **MSVC Build Tools** (Tauri linker) | `(Get-Command link.exe -ErrorAction SilentlyContinue) -ne $null` or `cd configurator; npm run tauri info` | auto-system | `winget install --id Microsoft.VisualStudio.2022.BuildTools -e --silent --accept-source-agreements --accept-package-agreements --override "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"` (multi-GB; first run is slow) |
| 12 | **WebView2 runtime** | `Test-Path 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}'` | bundled-w11 | bundled with Windows 11; if absent: `winget install --id Microsoft.EdgeWebView2Runtime -e --silent --accept-source-agreements --accept-package-agreements` |
| 13 | **Configurator icon** (placeholder OK) | `Test-Path configurator\src-tauri\icons\icon.ico` | auto-repo | generate from a placeholder PNG via `cd configurator; npm run tauri icon -- ../docs/installuidraft/.../placeholder.png` (or commit a stub `icon.ico`); blocks `cargo build` otherwise |
| 14 | Repo has **`area:addon`** and **`area:configurator`** labels | `gh label list --json name --jq '.[].name' \| Select-String '^area:(addon\|configurator)$'` returns both | auto-repo | `gh label create area:addon --color 0E8A16 --description "Kodi add-on (Python)" --force; gh label create area:configurator --color 5319E7 --description "Windows configurator (Tauri 2)" --force` |

Rows are checked in order; a missing row at any tier is acted on per its tier rule
described above. There is no database; no external services to verify. (Memory note
`tauri-env-installed` records that rows 10/11 already passed on 2026-05-29; row 13 is the
known blocker tracked in `configurator-icon-files-missing`.)

---

# §3 Work in progress (resume here first)

> **Read this FIRST on `resume`.** §3a covers Addon work, §3b covers Configurator work.
> Maintained by `done for the day` — each subsection is overwritten independently. If a
> subsection is empty (`(none)`), that area ended clean; offer the operator a fresh theme
> in that area.

## §3a Addon work — in progress

**As of 2026-05-29 (end of day):** (none in flight)

- Last addon release: **v2.9.13** on `main`. Next staged release is **v2.9.14** on branch
  `wip/wizard-ux` (first-run wizard fixes, PO headers, one-click setup-file install,
  expanded player presets) — operator needs to verify on the CoreELEC box per
  [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](docs/MANUAL_VERIFICATION_CHECKLIST.md), then
  `/release 2.9.14`.
- **Recent activity:** issue [#22](https://github.com/skull-01/script.oppo203.iso.external/issues/22)
  ([Bug]: wizard launch failure, `No module named 'wizard'`, `type:bug`) was closed
  2026-05-28 — that's the bare-import gotcha (§7.1 in
  [`docs/ai-handoff/AI_RESUME_GUIDE.md`](docs/ai-handoff/AI_RESUME_GUIDE.md)) whose fix
  lives on `wip/wizard-ux`. **#22 has no `area:` label yet** — needs `area:addon`
  back-applied on next `resume` (or as part of cutting v2.9.14).
- **Candidate themes for next addon session** (pick one, per §4):
  1. **Cut v2.9.14** — run `/release 2.9.14` once `wip/wizard-ux` is operator-verified
     on-device. Tag-driven via `package.yml`; 8-doc evidence set; styled notes.
  2. **Fix the broken `claude-review` CI check** — partially done via PR #29 (allowed_bots
     config); next real-bot run lands ~2026-06-03 with the weekly dependabot batch.
  3. **Back-apply `area:addon` to #22** and any future bug issues, so the per-area
     reporting in §1 stays honest.

## §3b Configurator work — in progress

**As of 2026-05-29 (end of day):**

- **PR #30 — *Scaffold OppoKodiAddon Configurator (Tauri 2 + React)*** — **MERGED** at
  `394f9fc` on `main`. Tauri 2 + Vite + React + TS shell under `configurator/`, Direction
  A "Warm Paper" tokens, persistent shell, all 23 wizard screens ported, `tsc --noEmit` +
  `vite build` clean. The scaffold theme is done.

- **Four follow-up PRs are open and need triage** (all draft, all created 2026-05-28
  before today's spine revision — none carry `area:configurator` labels yet, back-apply
  on next `resume`):
  - [#33 DRAFT](https://github.com/skull-01/script.oppo203.iso.external/pull/33)
    `configurator: wire window-control IPC on custom title bar` —
    `claude/window-control-ipc-7q3xt`. Implements what was the §3b candidate-theme #2.
  - [#34 DRAFT](https://github.com/skull-01/script.oppo203.iso.external/pull/34)
    `configurator: persist WizardState to %APPDATA% across restarts` —
    `claude/state-persistence-n3p2w`. Implements what was the §3b candidate-theme #3.
  - [#35 DRAFT](https://github.com/skull-01/script.oppo203.iso.external/pull/35)
    `configurator: unblock first-time cargo build (icon + lockfile + winget docs)` —
    `claude/configurator-build-setup-k8m2x`. Addresses §2a row 13 (icon stub) and the
    `configurator-icon-files-missing` memory.
  - [#32 DRAFT](https://github.com/skull-01/script.oppo203.iso.external/pull/32)
    `docs: align AGENTS.md ruff target with CI; refresh handoff §3 for #30 merge` —
    `claude/doc-cleanup-r8m1d`. **Overlaps today's spine revision** — the §3 refresh
    part is now redundant; the AGENTS.md ruff-target alignment may still be useful.
    Reviewer should cherry-pick or close.
  - [#36 OPEN](https://github.com/skull-01/script.oppo203.iso.external/pull/36)
    `docs: end-of-day handoff 2026-05-29 (mid-day continuation)` —
    `claude/eod-handoff-q9p2r`. A stale mid-day EOD that didn't account for today's
    spine revision. Likely close in favor of today's EOD commit.

- **This session revised the `resume` procedure for two work areas** (no configurator
  code touched):
  - Split §1 into addon + configurator parallel reporting; added `area:addon` /
    `area:configurator` labels (auto-created by §2a row 14).
  - Rewrote §2a for Windows with `auto-system` winget installs for rows 1, 3, 7, 10, 11,
    12; added row 13 (icon stub — overlaps with PR #35) and row 14 (area labels).
  - Split §3 into §3a (addon) / §3b (configurator) so `done for the day` overwrites each
    independently.
  - Updated [`AGENTS.md`](AGENTS.md), [`docs/ai-handoff/AI_RESUME_GUIDE.md`](docs/ai-handoff/AI_RESUME_GUIDE.md)
    §9, [`.claude/commands/resume.md`](.claude/commands/resume.md), and the project memory
    (`tauri-env-installed`, `MEMORY.md` session-continuity bullet) for consistency.

- **Candidate themes for next configurator session** (pick one, per §4):
  1. **Triage the four open draft PRs** (#32, #33, #34, #35) — close #32's §3-refresh
     portion as redundant; decide whether #33/#34/#35 are ready to be promoted out of
     draft. Likely the cleanest first move now that #30 is in.
  2. **Promote one of #33/#34/#35 to ready** after spot-checking the diff and applying
     the `area:configurator` label.
  3. **Real side effects** behind the diag logs (SFTP probe for Tier A, SMB probe for
     Tier B, TCP port knock for TV-backend detection, OPPO `#EJT`/`#QPW` over port 23) —
     multi-PR theme, its own session, blocked on #33 (IPC) and #34 (state) landing first.
  4. **File generation** for `playercorefactory.xml` + remote-bridge keymap.
  5. **App icon + bundling** before any release build — covered by #35.

- **Blockers:** none. §17a cache remains empty; the four open configurator PRs are not
  in §17a because they're PRs, not Issues. **No `area:` labels are applied to anything
  yet** (#22, #32-#36 all unlabeled) — next `resume` will auto-create the labels via §2a
  row 14, but back-applying them to existing items is a manual triage step.

---

# §4 Build norms

- **Session shape — one theme per session, soft cap ≤ 4 PRs.** Mixing themes within a
  session is where bugs slip in (proven in retros). If the operator nudges into a second
  theme, suggest finishing the current one and resuming next session.
- **No inline code comments by default.** Add only when the WHY is non-obvious (subtle
  invariant, workaround for a specific bug). Never explain WHAT — identifiers do that.
- **Lint/test backstop** — `pytest -n auto` + `ruff check .` must pass before promoting a
  PR out of draft. For configurator changes: `npx tsc --noEmit && npm run build` too.
- **Honest signature** — claim only what was actually run in this session. "Code compiles"
  ≠ "feature works". Distinguish typecheck / unit-tested / clicked-through / verified by
  operator. Never weaken the project's
  **"software-verified / hardware validation not claimed"** wording.
- **Scope discipline** — don't refactor adjacent code. Don't add features, abstractions,
  fallbacks, or validation the task doesn't require. Smallest possible diff.
- **Test link norm** — every completed change ends with one copy-paste line (run command
  or unittest command) + URL.
- **Only the operator closes issues** — never `gh issue close`, never `Closes #N`. Comment
  the SHA on the issue and add a verification step to
  [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](docs/MANUAL_VERIFICATION_CHECKLIST.md).

---

# §5 Architecture overview

_to fill — high-level: Kodi add-on (Python) + Windows configurator (Tauri 2 + React/TS) +
how the two pieces relate (configurator drives the add-on's existing
`resources/lib/installer.py` over SSH/SMB)._

# §6 Module map — add-on (Python)

_to fill — `default.py` / `service.py` entry points; `resources/lib/` modules
(oppo_control, avr_*, transfer file generation, installer, etc.)._

# §7 Module map — configurator (Tauri/React)

_to fill — `src-tauri/` Rust shell + `src/` React tree (shell/, screens/, state.ts,
steps.ts)._

# §8 Data model

_to fill — WizardState shape; add-on settings keys; `playercorefactory.xml` +
keymap schemas._

# §9 Key flow — Kodi handoff

_to fill — what happens when Kodi launches a UHD ISO; how the add-on routes to OPPO; the
TV input switch._

# §10 Key flow — configurator session

_to fill — 6-step wizard (Step 0 prereq → 1 Kodi box → 2 TV → 3 Player → 3.5 Inputs →
Test) and the state persistence boundary._

# §11 OPPO / clone control protocol

_to fill — port 23 IP control; `#PON` vs `#EJT` (clone wake-rewrite); `#QPW` query._

# §12 TV control backends

_to fill — adb / roku_ecp / sony_bravia / smartthings / lg_command / samsung_command /
custom_command; the basic-control-test gate; the ADB-weak input-finding fallback funnel._

# §13 Packaging boundaries

_to fill — `tools/package_installable_zip.py` allowlist (only addon.xml + default.py +
service.py + resources/ ship); how `configurator/` stays excluded; release evidence in
`release-evidence/`._

---

# §14 Gotchas (accumulate as hit)

_Format: `### YYYY-MM-DD — short title` · what bit us · how we recovered · how to prevent._

### 2026-05-29 — `build\_tmp` from the Windows pytest TEMP workaround can leave OS-locked dirs that break `audit_release.py`

- **What bit us:** an earlier session had used the historical Windows workaround
  (`$env:TEMP = build\_tmp; $env:TMP = $env:TEMP`) before running pytest. A handful of
  `build\_tmp\tmpXXXXXXXX\` subdirs ended up with ACLs that denied `Remove-Item`, `cmd
  rmdir /s/q`, `takeown /f`, and `icacls /grant` even from a normal user shell — likely
  Defender / a file-indexer holding handles. `tools/audit_release.py` walks the repo and
  prints `Can't list 'C:\…\build\_tmp\tmpXXX'` to stdout when it hits one; that line
  precedes the JSON payload and breaks two tests that call the audit CLI with `--json`:
  `tests/test_v291_build10_audit_reporter_refactor.py::test_audit_cli_json_output_still_works`
  and `tests/test_all.py::TBuild5ReleaseAuditArtifacts::test_release_audit_cli_json`.
- **How we recovered:** since the lock could not be cleared without admin/reboot,
  `Move-Item build\_tmp $env:USERPROFILE\build_tmp_LOCKED_delete_after_reboot` (rename
  only needs parent write access, not contents access) moved it out of the repo; the two
  tests then passed. Locked tree can be deleted with `rmdir /s/q` after the next reboot
  frees the handles.
- **How to prevent:** the full suite passed this session in ~8.5s **without** the
  `$env:TEMP=build\_tmp` override (just `--basetemp="build\_pt"` and
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`). The override may no longer be necessary on this
  machine. Try without it first; only reach for it if `WinError 5` (or a similar
  permission-denied) actually appears, and prefer routing TEMP to a path **outside the
  repo** (e.g. a freshly created `$env:USERPROFILE\.pytest-tmp`) so the audit walker
  cannot reach it.

---

# §15 Development journey

_Append-only, newest-last. One bullet per material commit or session-shaping decision._

- **2026-05-28** — Scaffolded the Windows configurator under `installer/` (Tauri 2 + Vite +
  React + TS, Direction A "Warm Paper" tokens). PR #30 opened as draft.
- **2026-05-28** — Renamed `installer/` → `configurator/` plus all identifiers (npm
  package, Cargo crate, Tauri bundle id) because the app *configures* an already-installed
  add-on; "installer" was a misnomer carried from the design handoff.
- **2026-05-28** — Ported all 21 remaining wizard screens from
  `docs/installuidraft/design_handoff_oppo_installer/prototype/` into typed TSX
  (`screens/step1.tsx` through `screens/test.tsx`). Bundle: 47 modules / 215 KB JS / 25 KB
  CSS.
- **2026-05-28** — Bootstrapped this AI handoff + agent norms structure
  (`CLAUDE.md`, `AGENTS.md`, `AI_RESUME_HANDOFF.md`, `docs/MANUAL_VERIFICATION_CHECKLIST.md`)
  per operator's job_finder_ri norms. Existing spine docs replaced wholesale. Issue model
  set to hybrid (Issues for bug/enhancement tracking, PRs for delivery).

---

# §16 Open questions (strategic decisions blocking work)

(none open)

_Add as: `### YYYY-MM-DD — title` · context · the decision needed · who decides._

---

# §17 Backlog audit — narrative

_Current state of every open issue, with one-line context per issue. Maintained by the
operator + on-demand via the `backlog audit` trigger. Empty until first issues filed under
the hybrid model._

(none)

---

# §17a Backlog audit cache

_Refreshable snapshot queried by the `backlog audit` trigger. Agents read from here first
before re-scanning live GitHub state (operator norm #10). The `Area` column is the
`area:addon` / `area:configurator` label that drives the per-area split in §1._

Last refreshed: **never** (no issues yet).

| # | Title | Area | Labels | State | Implementing SHA(s) | Operator-verified? |
|---|---|---|---|---|---|---|
| _empty_ | | | | | | |

---

# §18 Reserved

_(intentionally empty — preserved for future use)_

---

# §19 Updates to this document

_Meta-log of changes to this handoff itself. Dated, newest-last. Maintained by
`done for the day`._

- **2026-05-28** — Bootstrapped from scratch per operator's job_finder_ri norms. Replaced
  the prior 397-line PR-only handoff. Sections §1 / §2 / §2a / §3 / §4 filled; §5–§17a /
  §19–§21 seeded as headers.
- **2026-05-28 (EOD)** — First `done for the day` cycle. Refreshed §3 to point at PR #30
  awaiting review + the chain of follow-up themes; both branches confirmed pushed and in
  sync with origin (`main`@`636ae35`, `claude/windows-installer-ui-gfv4m`@`edba3d1`). No
  issues opened/closed/retitled — §17a cache remains empty.
- **2026-05-29 (EOD)** — Verification + cleanup session, no code changes. Refreshed §3
  to record today's work (claude-review CI fix verified to the limit of what can be
  proven before the next dependabot batch; memory hygiene); added the first §14 Gotcha
  (`build\_tmp` Windows-locked tmpdirs vs. `audit_release.py`); updated the header
  "Last sync" / "Tests on `main`" to `4e54c5d` / 987 passed, 3 skipped. PR #30 unchanged.
  §17a still empty (no issues opened/closed/retitled).
- **2026-05-29** — **Revised `resume` procedure for two work areas.** §1 now reports
  *Addon* and *Configurator* independently (last-5-created, last-5-closed, WIP, theme
  recommendations); driven by new `area:addon` / `area:configurator` GitHub labels
  filtered via `gh issue list --label area:<area>`. §2a was rewritten for Windows
  (PowerShell checks + `winget install` for `auto-system` rows: git, Python, Node, Rust,
  MSVC Build Tools, WebView2) and gained two new rows: 13 (configurator icon placeholder
  — already tracked by `configurator-icon-files-missing` memory) and 14 (the two area
  labels). §3 was split into §3a (addon) and §3b (configurator); today's configurator-
  only WIP moved into §3b verbatim, §3a seeded with the v2.9.14 candidate theme so the
  next `resume` has both branches populated. §17a cache gained an `Area` column. AGENTS.md
  updated with a one-line area-label norm.
- **2026-05-29 (EOD #2 — done for the day)** — End-of-day after the spine revision
  above. Header "Last sync" updated from `4e54c5d` to `394f9fc` (origin/main; the merge
  of PR #30 configurator scaffold which landed mid-day between today's first EOD and
  this one). Tests `pytest -n auto`: **987 passed, 3 skipped in 11.07s** (parallel; no
  TEMP override needed per §14). Refreshed §3a to record closure of issue #22 (the
  wizard `No module named 'wizard'` bug; fix on `wip/wizard-ux` staged for v2.9.14).
  Rewrote §3b for the new world: PR #30 is **merged**; four follow-up draft PRs
  (#32, #33, #34, #35) and one stale EOD continuation (#36) are now open and need
  triage — #32 overlaps today's §3 refresh, #33/#34/#35 implement what were §3b's
  candidate themes 2/3/6. No `area:` labels back-applied yet to #22/#32-#36 — flagged
  as the next-`resume` triage step. §1, §2, §2a, §4–§17a, §19, §20–§21 unchanged
  beyond this entry. `docs/ai-handoff/AI_RESUME_GUIDE.md` §9 also updated to point at
  this spine and stop describing the old single-list `resume` flow.

---

# §20 Dev notes (operator's verbatim instructions)

_Append-only. Each entry: `### YYYY-MM-DD HH:MM — dev note` followed by the operator's
text VERBATIM. No summarizing, no editing. Added via the `dev note:` trigger._

(none yet)

---

# §21 Questions log

_Q&A pairs from substantive conversations (clarifying scope, picking between approaches,
defining terminology). Append after each substantive turn. Newest-last._

### 2026-05-28 — Aesthetic + stack + repo layout for the configurator

- **Q:** Which tech stack should we build the configurator in?
  **A:** Tauri 2 (Rust + web UI) — natural port from the React/CSS prototype.
- **Q:** Where should the configurator code live?
  **A:** Subdirectory in this repo (`configurator/`).
- **Q:** Which aesthetic direction?
  **A:** Direction A — Warm Paper (default per design handoff).

### 2026-05-28 — Naming

- **Q:** Is "installer" the right word?
  **A:** No — the Kodi add-on is installed by Kodi; this Windows app *configures* the
  already-installed add-on. Renamed everything to "OppoKodiAddon Configurator" / verb
  "configure" / "set up". Directory `installer/` → `configurator/`.

### 2026-05-28 — Issue model under the new handoff

- **Q:** GitHub Issues, PR-only, or hybrid?
  **A:** Hybrid — Issues for bug/enhancement tracking, PRs for delivery.
