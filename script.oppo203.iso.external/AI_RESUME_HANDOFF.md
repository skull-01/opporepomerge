# AI_RESUME_HANDOFF.md — session continuity for `script.oppo203.iso.external`

**Audience:** any AI agent (Claude, Cursor, Codex, …) starting or resuming work on this
repo. Read this file **first**. Treat live code + `git`/`gh` output as authoritative; this
file is the map and the memory.

**Repo:** `github.com/skull-01/script.oppo203.iso.external` · **Default branch:** `main`
**Last sync:** commit `7b65ed2` (origin/main, 2026-05-29 — docs: end-of-day handoff 2026-05-29 (strip-wizard session)) · **Tests on `main`:** 987 passed, 3 skipped (`pytest -n auto`, ~11s)
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

When the operator types **`resume`** (alone), do exactly this:

1. **Read this file** (especially §3 "Work in progress") and the repo instruction files
   ([`AGENTS.md`](AGENTS.md), [`CLAUDE.md`](CLAUDE.md), [`CONTRIBUTING.md`](CONTRIBUTING.md)).
2. **Run the environment readiness check** in §2a. Print a small readiness table.
   - All rows green → one line `Environment: ready ✓` and continue.
   - An *auto* row missing → install it (idempotent), re-check, report what was installed.
   - An *auto (UAC)* row missing → **warn the operator a UAC dialog is about to appear**,
     trigger the install via `Start-Process -Verb RunAs`, then re-check.
   - A *manual* row missing → print the exact fix command and **STOP**.
3. **Report recent backlog activity** — *last 5 issues created* and *last 5 issues closed*,
   each shown as `#N <short title snippet>` per the operator's "list issues with titles"
   norm. Use `gh issue list --limit 5 --state all --sort created` and
   `gh issue list --limit 5 --state closed --sort updated`.
4. **Suggest 1–3 themes** (one theme = one session, per the session-shape rule in §4). Lead
   with any unfinished entry in §3 "Work in progress". **STOP and wait** for the operator
   to pick a theme before doing any new work.

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
2. **Update §3 "Work in progress"** — overwrite with the current state: what's in flight,
   the clean stopping point for tomorrow, any blockers.
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

The readiness check verifies the operator's machine can edit, test, and build both the
add-on (Python) and the Windows configurator (Node + Rust + Tauri 2).

| Row | Prereq | How to check | Auto-installable? | Fix command if missing |
|---|---|---|---|---|
| 1 | **git** ≥ 2.30 | `git --version` | manual | install from package manager |
| 2 | **`gh` CLI** authenticated | `gh auth status` | manual | `gh auth login` (operator) |
| 3 | **Python** 3.9+ | `python3 --version` | manual | install from python.org / pyenv |
| 4 | Repo **`.venv`** | `test -d .venv` | **auto** | `cd /home/user/script.oppo203.iso.external; python3 -m venv .venv` |
| 5 | **Python dev deps** | `.venv/bin/python -m pytest --version` | **auto** | `cd /home/user/script.oppo203.iso.external; .venv/bin/python -m pip install -r requirements-dev.txt paramiko` |
| 6 | **paramiko** (SSH probes) | `.venv/bin/python -c "import paramiko"` | **auto** | covered by row 5 |
| 7 | **Node** 20+ | `node -v` | manual | install from nodejs.org / nvm |
| 8 | **npm** 10+ | `npm -v` | manual | bundled with Node |
| 9 | configurator **`node_modules`** | `test -d configurator/node_modules` | **auto** | `cd /home/user/script.oppo203.iso.external/configurator; npm install` |
| 10 | **Rust toolchain** 1.77+ (`cargo`, `rustc`) | Windows: `Test-Path "$env:USERPROFILE\.cargo\bin\cargo.exe"` · POSIX: `command -v cargo` | **auto** | **Windows:** `winget install --id Rustlang.Rustup --silent --accept-package-agreements --accept-source-agreements` (default scope only; `--scope user` fails for this package) · **POSIX:** `curl https://sh.rustup.rs -sSf \| sh` |
| 11 | (Windows only) **WebView2 runtime** for Tauri 2 webview | `Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -ErrorAction SilentlyContinue` returns non-null | manual | Ships with Windows 11; on older Windows install the Evergreen Bootstrapper: `winget install --id Microsoft.EdgeWebView2Runtime --silent --accept-package-agreements --accept-source-agreements` |
| 12 | (Windows only) **MSVC Build Tools 2022** with C++ workload — Rust's `x86_64-pc-windows-msvc` toolchain links against `link.exe` | `Test-Path "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC"` | **auto (UAC)** | `Start-Process -Verb RunAs -FilePath powershell -ArgumentList '-NoProfile','-Command','winget install --id Microsoft.VisualStudio.2022.BuildTools --silent --accept-package-agreements --accept-source-agreements --override "--quiet --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"'` — first install triggers a Windows UAC dialog; **operator must click Yes**. Subsequent resumes skip (idempotent). |

**Notes on auto-install behavior:**

- Plain **auto** rows install silently with no prompt; safe to run on every resume.
- Rows marked **auto (UAC)** install on resume if missing, but trigger a Windows UAC dialog the first time; once installed, future resumes detect it and skip. Inform the operator before the prompt fires so they're not blindsided.
- **PATH gotcha on Windows after row 10 installs:** the cargo bin dir (`$env:USERPROFILE\.cargo\bin`) is NOT on the inherited PATH of fresh `PowerShell` tool calls until a shell restart. Prefix every cargo invocation in the same session as the install with `$env:PATH = "$env:USERPROFILE\.cargo\bin;" + [Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH","User"); ` or call cargo by full path.
- **Manual** rows print their fix command and STOP — the agent will not install anything that needs the operator to provide credentials, sign in to a service, or make a judgment about a system-wide change other than UAC consent.

**What "build the Windows binary" needs end to end:** rows 7 (Node), 8 (npm), 9 (node_modules), 10 (Rust), 11 (WebView2), 12 (MSVC). For `cargo build` / `npm run tauri dev` (development) — that's the full list. For `npm run tauri build` (production .msi/.exe bundle) — same, plus WiX 3.x and NSIS, but Tauri 2 auto-downloads both on first bundle run, so neither needs an §2a row.

Auto rows install on `resume` if missing. Manual rows print their fix command and STOP.
There is no database; no external services to verify.

---

# §3 Work in progress (resume here first)

> **Read this FIRST on `resume`.** Maintained by `done for the day`. If empty, the last
> session ended clean; offer the operator a fresh theme.

**As of 2026-05-29 (end of day — config-owner-policy session, second EOD of the day):**

- **Addon area today — PR [#45](https://github.com/skull-01/script.oppo203.iso.external/pull/45)
  *docs: 'configurator owns add-on configuration' policy (ENH-#41 part A)*** is
  open as a **draft** on `claude/config-owner-policy-a3k7m2nq` (tip `1ed15a3`).
  - Commit `1ed15a3` is a 3-file docs-only change (+70 / −1):
    - [`AGENTS.md`](AGENTS.md): new `## Configuration is owned by the configurator`
      section after `## Scope discipline`. Lists allowed in-add-on exceptions
      (per-session toggles, the #42 settings-menu carve-out, diagnostic
      exports already in `installer.main()`) and not-allowed-without-sign-off
      (new persistent-setting categories, new first-run dialogs, add-on side
      writers for `playercorefactory.xml` / keymap / NAS creds).
    - [`CONTRIBUTING.md`](CONTRIBUTING.md): matching `## Configuration ownership`
      section between `## Ground rules` and `## Local checks`, framed for
      external contributors. Same policy + exceptions.
    - [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](docs/MANUAL_VERIFICATION_CHECKLIST.md):
      Phase A entry asking the operator to confirm the policy + the three
      allowed exceptions + the not-allowed list match their intent.
  - Implementing SHA `1ed15a3` commented on
    [#41](https://github.com/skull-01/script.oppo203.iso.external/issues/41)
    per the only-operator-closes-issues norm.

- **Tests on the policy-doc branch:** `pytest -n auto --basetemp=build\_pt` =
  **987 passed, 3 skipped** in ~11s. Pre-push hook (parallel + coverage gate,
  99% floor): **987 passed, 3 skipped** in 14.65s; coverage **99.08%**. Docs-only
  change, no behavioural impact — feature branch matches main's test result.

- **Parts B + C of #41 deferred to next session — both wait on PR #40.** Per
  this session's sequencing Q&A (now logged in §21): Part A docs ship now from
  `main` (no overlap with #40). Parts B + C touch `resources/settings.xml`,
  which PR #40 also renames (`<category id="wizard">` → `<category id="playback">`)
  and modifies (`wizard_mode` removed) — doing them now would create avoidable
  merge friction.
  - **Part B** (in-add-on guidance hint on settings open): per operator's
    "Both" choice — static label at top of `resources/settings.xml` *plus*
    `service.py` first-open-per-session `xbmcgui.Dialog().notification`
    tracked via `xbmcgui.Window(10000)` property (clears on Kodi restart).
  - **Part C** (settings-file ownership marker): configurator writes
    `<!-- generated by configurator vX.Y.Z YYYY-MM-DD -->` in `settings.xml`;
    add-on warns when a configurator-managed key is overwritten via Kodi's UI.
  - Acceptance for #41 stays open until B + C land.

- **Still in flight (carried over from prior session):**
  - PR [#40](https://github.com/skull-01/script.oppo203.iso.external/pull/40)
    (strip-wizard) — draft on `claude/strip-wizard-g4feovqi`, mergeable
    `CLEAN`. Awaiting operator review of the diff (especially the
    `Monitor.onSettingsChanged` removal — the headline behavioural change) +
    Phase A on-device verification. **#40's Phase A entry lives on its own
    branch (`92a9408`); it will appear in `main`'s
    `docs/MANUAL_VERIFICATION_CHECKLIST.md` only after #40 merges.**
    `main`'s checklist currently shows just the #45 Phase A row (from this
    EOD commit).
  - Six addon-area issues open: #38 (ruff backlog), #41 (parent of #45 —
    stays open until B + C also land), #42 (settings menu), #43 (lib split),
    #44 (hardware testing).
  - Configurator drafts #32 / #33 / #34 / #35 unchanged since 2026-05-29.
  - Spine revision PR [#37](https://github.com/skull-01/script.oppo203.iso.external/pull/37)
    still open — once merged it will introduce the §3a/§3b split.

- **Candidate themes for next session** (pick one, per §4):
  1. **Operator review + merge PR #40, then #45, then #41 Parts B + C.** Finishes
     the configurator-owns-config theme started across the last two sessions.
     Highest-leverage path; everything below depends on the policy contract.
  2. **ENH-#43 — split `resources/lib` into TV/Oppo/AVR/Kodi sub-packages.**
     Best done *before* #42 so the in-add-on settings menu lands in the right
     layout from day one. Independent of #45.
  3. **ENH-#42 — minimal in-add-on settings menu.** Depends on #43's layout
     and #41's policy doc landing.
  4. **#38 ruff backlog PR 1 (auto-fix sweep).** Independent of all of the
     above; can run in a parallel session.
  5. **Configurator triage** (different area) — work through #32 / #33 / #34
     / #35.

- **No active blockers.** Six addon-area issues in §17a; #45 added to the
  table this EOD as the implementing PR for #41 part A.

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
before re-scanning live GitHub state (operator norm #10)._

Last refreshed: **2026-05-29 (EOD — config-owner-policy)**.

| # | Title | Area | Labels | State | Implementing SHA(s) | Operator-verified? |
|---|---|---|---|---|---|---|
| 22 | [Bug]: wizard launch failure (`No module named 'wizard'`) | addon | `bug`, `area:addon` | CLOSED 2026-05-28 | `b7471db` on `wip/wizard-ux` (wizard now removed entirely by `3abf486` on `claude/strip-wizard-g4feovqi`) | closed by operator |
| 38 | ENH-: clear ruff backlog on main (336 errors, 172 auto-fixable, 66% in 3 test files) | addon | `area:addon` | OPEN | — | not started |
| 41 | ENH-: configurator owns add-on configuration; add-on is read-mostly | addon | `area:addon` | OPEN | `1ed15a3` (Part A only) on `claude/config-owner-policy-a3k7m2nq` — [PR #45](https://github.com/skull-01/script.oppo203.iso.external/pull/45) draft. Parts B + C pending after PR #40 merges. | Phase A queued |
| 42 | ENH-: minimal in-add-on settings menu (TV/OPPO/AVR/Kodi IPs + language) | addon | `area:addon` | OPEN | — | not started |
| 43 | ENH-: split `resources/lib` into TV / Oppo / AVR / Kodi sub-packages | addon | `area:addon` | OPEN | — | not started |
| 44 | ENH-: hardware-validation testing — lending, donations, tester reports wanted | addon | `area:addon` | OPEN | — | not started |

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
- **2026-05-29 (EOD — strip-wizard session)** — End-of-day after a single-theme
  addon session that stripped the in-Kodi setup wizard from the add-on. PR
  [#40](https://github.com/skull-01/script.oppo203.iso.external/pull/40) on
  `claude/strip-wizard-g4feovqi` (tip `92a9408`) is open as draft. 44 files
  changed, +313 / −5814. Tests: **865 passed, 3 skipped** in ~10s on the strip
  branch; coverage **99.05%** (≥ 99% floor). Filed 4 new `area:addon` ENH
  issues — #41 configurator-owns-config policy, #42 in-add-on settings menu,
  #43 module split (TV/Oppo/AVR/Kodi), #44 hardware-testing solicitation.
  Created [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) on `main` (commit
  `3967cb6`) with the strategic direction + open-issue grid + suggested
  ordering. Header "Last sync" updated from `4e54c5d` to `3967cb6`; tests on
  `main` re-confirmed at **987 passed, 3 skipped** in ~12s (unchanged — the
  strip work is on a feature branch). §3 rewritten to record the strip-wizard
  PR + new issues; §17a backlog cache populated for the first time (with
  Area column added) — six rows: #22 (closed), #38, #41, #42, #43, #44.
  Operator's spine revision PR
  [#37](https://github.com/skull-01/script.oppo203.iso.external/pull/37)
  remains open and unmerged on `main`; when it lands it will introduce the
  §3a/§3b split and the rewritten §2a — at that point the next EOD reconciles
  whatever drift this entry created.
- **2026-05-29 (EOD — config-owner-policy session)** — **Second** `done for
  the day` cycle on 2026-05-29, after the strip-wizard EOD at `7b65ed2`.
  Single-theme addon session that drafted **Part A** (policy doc) of
  [ENH-#41](https://github.com/skull-01/script.oppo203.iso.external/issues/41).
  PR [#45](https://github.com/skull-01/script.oppo203.iso.external/pull/45) on
  `claude/config-owner-policy-a3k7m2nq` (tip `1ed15a3`) opened as draft.
  3 files changed, +70 / −1: [`AGENTS.md`](AGENTS.md) gained
  `## Configuration is owned by the configurator`,
  [`CONTRIBUTING.md`](CONTRIBUTING.md) gained `## Configuration ownership`
  (matching policy framed for external contributors),
  [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](docs/MANUAL_VERIFICATION_CHECKLIST.md)
  gained a Phase A row for the #45 review. Tests on the policy-doc branch:
  **987 passed, 3 skipped** in 10.69s (`pytest -n auto --basetemp=build\_pt`);
  pre-push hook with coverage gate: **987 passed, 3 skipped** in 14.65s,
  coverage **99.08%**. SHA `1ed15a3` commented on issue #41 per the
  only-operator-closes-issues norm. Parts B + C of #41 deferred to the next
  session — both touch `resources/settings.xml`, which PR #40 also modifies,
  so doing them now would create avoidable merge friction. §3 rewritten to
  record PR #45 + the carried-over state of PR #40; §17a row for #41 updated
  with `1ed15a3` (Part A) and "Phase A queued"; §21 gained the sequencing +
  hint-mechanism Q&A from this session. Header "Last sync" updated from
  `3967cb6` to `7b65ed2`. No new gotchas (§14 unchanged). No new issues
  opened or closed.

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

### 2026-05-29 — Sequencing ENH-#41 against PR #40; in-add-on guidance hint mechanism

- **Q:** Should ENH-#41 (configurator-owns-config) ship as one PR or be split
  against PR #40 (strip-wizard, still draft)?
  **A:** Split into three parts. **Part A** (policy doc to
  [`AGENTS.md`](AGENTS.md) + [`CONTRIBUTING.md`](CONTRIBUTING.md)) ships now
  from `main` — no overlap with #40's diff. **Parts B** (in-add-on guidance
  hint on settings open) and **C** (settings.xml ownership marker) wait until
  #40 merges; both modify `resources/settings.xml`, which #40 renames
  (`<category id="wizard">` → `<category id="playback">`) and trims
  (`wizard_mode` removed). Doing B + C now would create avoidable merge
  friction.
- **Q:** For Part B's in-add-on guidance hint, which mechanism — a static
  label at the top of `settings.xml`, a `service.py` first-open-per-session
  `xbmcgui.Dialog().notification`, or both?
  **A:** Both. Static label is permanent visible guidance; the notification
  draws attention exactly once per Kodi session (tracked via
  `xbmcgui.Window(10000).setProperty(...)`, which clears on Kodi restart).
  Most code, strongest UX guarantee.
