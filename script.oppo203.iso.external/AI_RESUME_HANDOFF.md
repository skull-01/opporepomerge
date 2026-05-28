# AI_RESUME_HANDOFF.md — session continuity for `script.oppo203.iso.external`

**Audience:** any AI agent (Claude, Cursor, Codex, …) starting or resuming work on this
repo. Read this file **first**. Treat live code + `git`/`gh` output as authoritative; this
file is the map and the memory.

**Repo:** `github.com/skull-01/script.oppo203.iso.external` · **Default branch:** `main`
**Last sync:** commit `4e54c5d` (origin/main, 2026-05-29) · **Tests on `main`:** 987 passed, 3 skipped (`pytest -n auto`, ~8.5s)
**Latest release:** v2.9.13 · **Issue model:** **hybrid** — GitHub Issues for bug/enhancement
tracking, PRs for delivery.

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
| 10 | **Rust toolchain** 1.77+ | `cargo --version && rustc --version` (Windows: `& "$env:USERPROFILE\.cargo\bin\cargo.exe" --version`) | manual | **POSIX:** `curl https://sh.rustup.rs -sSf \| sh` · **Windows:** `winget install --id Rustlang.Rustup --silent --accept-package-agreements --accept-source-agreements` (default scope; `--scope user` fails for this package) |
| 11 | (Windows host only) **WebView2 + MSVC Build Tools 2022** for Tauri 2 | WebView2: ships with Win 11; MSVC: `Test-Path "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC"` | manual | `winget install --id Microsoft.VisualStudio.2022.BuildTools --silent --accept-package-agreements --accept-source-agreements --override "--quiet --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"` (needs UAC; trigger via `Start-Process -Verb RunAs`) |

Auto rows install on `resume` if missing. Manual rows print their fix command and STOP.
There is no database; no external services to verify.

**PATH gotcha on Windows after row 10 installs:** the cargo bin dir (`$env:USERPROFILE\.cargo\bin`) is NOT on the inherited PATH of fresh PowerShell tool calls until a shell restart. Prefix every cargo invocation with `$env:PATH = "$env:USERPROFILE\.cargo\bin;" + [Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH","User"); ` or call cargo by full path.

---

# §3 Work in progress (resume here first)

> **Read this FIRST on `resume`.** Maintained by `done for the day`. If empty, the last
> session ended clean; offer the operator a fresh theme.

**As of 2026-05-29 (end of day):**

- **PR #30 — *Scaffold OppoKodiAddon Configurator (Tauri 2 + React)*** — **still draft,
  awaiting operator review.** Branch `claude/windows-installer-ui-gfv4m` at `edba3d1`.
  Unchanged this session. State described in the 2026-05-28 EOD still applies: Tauri 2 +
  Vite + React + TS shell under `configurator/`, Direction A tokens, persistent shell, all
  23 wizard screens ported, `tsc --noEmit` + `vite build` clean.

- **`main` is at the SHA committed by this EOD** (the previous tip was `4e54c5d` from
  yesterday's EOD; today's commit is a handoff-doc-only update — no code change).

- **This session was verification + cleanup, no new feature work:**
  - **claude-review CI fix verified.** [#29](https://github.com/skull-01/script.oppo203.iso.external/pull/29)
    set `allowed_bots: 'dependabot'` in `.github/workflows/claude-code-review.yml`. The
    workflow runs cleanly on human PRs ([#30](https://github.com/skull-01/script.oppo203.iso.external/pull/30) — 3/3 green).
    The actual dependabot-actor path will be exercised on the next weekly batch
    (~2026-06-03 per `.github/dependabot.yml`); until then the fix is "config correct,
    awaiting first real bot run."
  - **Memory hygiene.** Deleted the obsolete `claude-review-workflow-reminder` memory
    (its own "How to apply" instructed deletion once fixed) and corrected the stale
    "No GitHub Issues" line in the Session-continuity memory entry to reflect the
    2026-05-28 switch to the hybrid issue model.
  - **Environmental cleanup.** Moved a leftover `build\_tmp` tree (locked Windows tmp
    dirs from earlier sessions) out of the repo to `~/build_tmp_LOCKED_delete_after_reboot/`
    so `tools/audit_release.py` stops walking it; the 2 audit JSON-CLI tests went
    green. The full suite was run **without** the historical `$env:TEMP=build\_tmp`
    workaround and passed in ~8.5s — the workaround may no longer be needed; see §14.

- **Clean stopping points for next session** (unchanged from yesterday; pick one theme,
  per §4):
  1. **Promote / merge PR #30** once the operator reviews the draft. The two follow-up
     PRs that naturally chain off it (window-control IPC, state persistence) need it
     merged first.
  2. **Wire window-control IPC** so the custom title bar's min/max/close actually do
     something. Small, ~1 PR. Branches off `main` once #30 is merged.
  3. **State persistence** to `%APPDATA%/OppoKodiAddonConfigurator/state.json`.
  4. **Real side effects** behind the diag logs (SFTP probe for Tier A, SMB probe for
     Tier B, TCP port knock for TV-backend detection, OPPO `#EJT`/`#QPW` over port 23).
     Multi-PR theme — would be its own session.
  5. **File generation** for `playercorefactory.xml` + remote-bridge keymap.
  6. **App icon + bundling** before any release build.

- **No active blockers.** No issues open under the hybrid model yet (none were filed this
  session); the §17a cache remains empty.

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

Last refreshed: **never** (no issues yet).

| # | Title | Labels | State | Implementing SHA(s) | Operator-verified? |
|---|---|---|---|---|---|
| _empty_ | | | | | |

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
