# AI_RESUME_HANDOFF.md — session continuity for `script.oppo203.iso.external`

**Audience:** any AI agent (Claude, Cursor, Codex, …) starting or resuming work on this
repo. Read this file **first**. Treat live code + `git`/`gh` output as authoritative; this
file is the map and the memory.

**Repo:** `github.com/skull-01/script.oppo203.iso.external` · **Default branch:** `main`
**Last sync:** commit `dce80cd` (origin/main, 2026-05-30) + this evening merge/release session (#96) · **PM-session 6-PR stack merged (#91–#96) + first configurator binary published** — `configurator-v0.1.0` is now a public GitHub **pre-release** (MSI + NSIS, unsigned, software-verified only); landed the Chinoppo `M9205 V1` split (#91), the build recipe (#94) + binary evidence (#95), the canonical Plan-format norm (#92), and the `BUILD_PLAN.md` refresh (#93) · **ENH-#51 mypy `--strict` rollout COMPLETE and now CLOSED by the operator** (gate **49/0**) · **Tests on `main`:** 943 passed, 3 skipped (`pytest -n auto`; coverage 99%; mypy `--gate` 49/0; per-PR CI green pre-merge incl. 3.9/3.10/3.12 smokes; `main`@`dce80cd` CI green) · **Configurator:** 64 vitest + `tsc -b`/`vite build` green this session (cargo not re-run; the published v0.1.0 binary built clean in the PM session)
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
| **`plan`** / **`create a plan`** / **`scope this`** | Produce a plan in the **canonical Plan format** ([`AGENTS.md`](AGENTS.md) → "Plan format"): ground against the current code first (confirm `file:line` anchors, flag already-done work), then **theme → per-PR scope blocks → dependency chain → 📊 rollup → ⚠️ risk callouts → verification regime → ✅ Go / 🛑 Wait / 🔁 Replan**. STOP for a Go before building. |
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

**PATH gotcha on Windows after row 10 installs:** the cargo bin dir
(`$env:USERPROFILE\.cargo\bin`) is NOT on the inherited PATH of fresh `PowerShell` tool
calls until a shell restart. Prefix every cargo invocation in the same session as the
install with `$env:PATH = "$env:USERPROFILE\.cargo\bin;" + [Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH","User"); `
or call cargo by full path.

Rows are checked in order; a missing row at any tier is acted on per its tier rule
described above. There is no database; no external services to verify. (Memory note
`tauri-env-installed` records that rows 10/11 already passed on 2026-05-29; row 13 was
satisfied by PR #35 merging the icon stub at `12e5b18`.)

---

# §3 Work in progress (resume here first)

> **Read this FIRST on `resume`.** §3a covers Addon work, §3b covers Configurator work.
> Maintained by `done for the day` — each subsection is overwritten independently. If a
> subsection is empty (`(none)`), that area ended clean; offer the operator a fresh theme
> in that area.

## §3a Addon work — in progress

**As of 2026-05-30 (evening — merge/release session; both areas touched).** **Clean
stopping point, no addon code in flight.** This session merged the 2026-05-30 PM session's
6-PR draft stack and published the first configurator binary (see §3b + §15). The addon-area
deliverable was:

- **Chinoppo `M9205 V1` split into a distinct hardware model** ([PR #91](https://github.com/skull-01/script.oppo203.iso.external/pull/91), merge `36f9cbd`): new `oppo_hardware_model` enum value `chinoppo_m9205_v1`, **appended** to `resources/settings.xml` (existing stored enum indices preserved) and mirrored through `settings_reader` / `hardware_profiles` / `hardware_capabilities` as an **exact `M9205` clone** (`#EJT` eject-to-wake, clone-safe, `http_api_436=False`); configurator `players.ts` re-pointed (plain `M9205` still → `chinoppo_m9205`); taxonomy count guards 17→18; new `tests/test_chinoppo_m9205_v1_split.py` (5 tests). Additive — **no behavior change to existing models.** PR-only (no tracked issue); Phase-A/C entry in the manual checklist. **Software-verified only** — the V1 mirror assumes identical protocol per the operator's confirmation; if real hardware shows it differs, its `HARDWARE_COMPAT` / profile entries need distinct values.

- **ENH-#51 mypy `--strict` rollout — COMPLETE and now CLOSED by the operator** (gate **49/0**; every `resources/lib` module + top-level `service.py`/`default.py` gated; CI `types` job enforces it). Nothing to resume. The full PR-by-PR history is in §15; recipe + all idioms (the no-redef strategy, `Settings.get -> Any`, conditional-Kodi-base `# type: ignore[misc]`, `X | None` over `Optional` for ruff `UP045`, the parallel-sub-agent technique) are in memory `mypy-strict-gate-rollout`.

- **Carried open (all `area:addon`, all merged & SHA-commented — awaiting operator close):**
  #38 (ruff), #42 (settings menu), #43 (lib split), #57 (fast test loop), #41 (incl. Part C
  config-side), #44 (solicitation — standing community call). Only the operator closes issues;
  Phase A/C on-device steps queued in `docs/MANUAL_VERIFICATION_CHECKLIST.md`. (**#51 is now
  closed** — the type-hardening arc is fully shipped and closed.)

- **Candidate themes for next addon session** (pick one, per §4):
  1. **Phase A/C on-device verification** of the merged work (incl. the M9205 V1 split) —
     operator action on real hardware, no agent code.
  2. **A net-new addon enhancement** — the type-hardening arc (ruff #38 → mypy #51) is
     complete and the configurator now owns config, so the addon is at a clean baseline.

## §3b Configurator work — in progress

**As of 2026-05-30 (evening — first configurator binary shipped + published).** **Clean
stopping point, no configurator work in flight, no open configurator PRs.** This session
merged the PM session's configurator stack and **published the first Windows binary** as a
public GitHub **pre-release**. **Software-verified only** — built + unit-tested, **not** run
in the live app, **no hardware validation** (Kodi box / OPPO / TV), **not** installed on a
clean machine.

- **First Windows binary — `configurator-v0.1.0` published** (public **pre-release**,
  unsigned; SmartScreen "unknown publisher" expected): MSI (3.15 MB) + NSIS setup (2.05 MB) +
  SHA-256 sidecars; tag `configurator-v0.1.0` at `dce80cd`. The add-on's `v2.9.13` stays the
  repo's "Latest"; this prerelease sits in the separate `configurator-v*` tag namespace.
  Delivered by the merged PM-session stack:
  - **Repeatable build recipe** ([PR #94](https://github.com/skull-01/script.oppo203.iso.external/pull/94), merge `60f7897`): `configurator/BUILD.md` (prereqs → `npm run dist` → outputs → versioning → signing), a `dist` npm alias, a `.gitattributes` pinning `Cargo.toml` to LF, and `src/version.test.ts` guarding that package.json / Cargo.toml / tauri.conf.json agree.
  - **Binary evidence** ([PR #95](https://github.com/skull-01/script.oppo203.iso.external/pull/95), merge `4af93b5`): `configurator/release-evidence/v0.1.0/BUILD_NOTES.md` + the published release notes (unsigned/SmartScreen caveat + SHA-256 verification steps).
- **Prior wizard-wiring (PR #68, `454e5ab`) unchanged** — the 7-slice wiring (mapping / TV-DB /
  generate / settings-merge / probes / Tier-A SSH / apply; see
  [`configurator/CONFIGURATOR_HANDOFF.md`](configurator/CONFIGURATOR_HANDOFF.md)), its 16
  `/code-review` bugs (#72–#87) fixed across #68/#88, ENH-#41 Part C provenance marker, 64 vitest
  tests. The 16 bugs remain **open, awaiting operator close** (Phase C on-device pending).
- **Chinoppo `M9205 V1` now split** to its own `chinoppo_m9205_v1` model (PR #91 — see §3a);
  the former "collapse to `chinoppo_m9205` pending confirmation" follow-up is **resolved**.
- **Prior merged scaffold (unchanged):** PR #30 scaffold, #33 window-control IPC, #34
  `%APPDATA%` state, #35 cargo-unblock + icon stub, #52 icon + first installers. Operator commit
  `384d180` added `configurator/CONFIGURATOR_HANDOFF.md` + an installer zip direct to `main`.

- **Resume here next (configurator):**
  1. **Install + smoke-test the published `v0.1.0` binary** on a clean Windows machine
     (MSI + NSIS), confirm launch + icon — operator action; the binary is build/unit-verified
     only (checklist entry already queued).
  2. **On-hardware verification** of the deploy paths (Tier A SSH+restart, Tier B SMB, Tier C
     copy) against a real Kodi box / OPPO / TV — operator action; software-verified only.
  3. **Grow the TV DB** at `docs/configurator/tv-db/tv-models.json` (seed is small, all
     `validated:false`; lineups carry the platform→backend mapping).
  4. **Real test ISO** — swap the placeholder once the asset exists (decision E).

- **Open `area:configurator` issues:** the 16 review bugs **#72–#87** (`type:bug`), all fixed +
  merged (PR #68 + #88), **awaiting operator close** (Phase C on-device pending). The wizard
  wiring (#68), the build recipe + binary (#94/#95), and the M9205 split (#91) were PR-only
  themes (no tracked issue).

---

# §4 Build norms

- **Session shape — one theme per session, soft cap ≤ 4 PRs.** Mixing themes within a
  session is where bugs slip in (proven in retros). If the operator nudges into a second
  theme, suggest finishing the current one and resuming next session.
- **Plans are deliverables, not sketches.** Any plan request (or any multi-PR theme)
  follows the **canonical Plan format** in [`AGENTS.md`](AGENTS.md): ground against the
  current code first (`file:line` anchors, flag already-done work), then theme → per-PR
  scope blocks (each with anchors + a `Tests:` line) → dependency chain → 📊 rollup →
  ⚠️ risk callouts → verification regime → **✅ Go / 🛑 Wait / 🔁 Replan**. Don't start
  building until the operator says Go.
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
- **2026-05-29** — ENH-#43: split the flat `resources/lib` (46 modules) into
  `tv/` / `oppo/` / `avr/` / `kodi/` sub-packages, canonical name
  `resources.lib.<bucket>.<module>`. A lazy `sys.meta_path` alias finder in
  `resources/lib/__init__.py` preserves legacy flat names (`resources.lib.X`
  and bare `X`) as same-object aliases during a deprecation window; `version.py`
  → `kodi/`. Draft PR #47. Established convention: module-top cross-family
  imports explicit (`from ..oppo… import`), lazy in-function imports bare
  (finder-resolved, mock-friendly).
- **2026-05-29** — Merged the two in-flight addon PRs onto `main`: **ENH-#43**
  lib split (PR #47 at `3ba5009`) and **ENH-#41 Parts B+C** configurator-owner
  hint (PR #46 at `f21033b`). The PRs overlapped on `service.py` /
  `tests/test_all.py` / the manual checklist despite the prior §3a "disjoint"
  note; integrated #46 onto the post-#47 `main` locally, ran the full gate on the
  combined tree (commit `126bac9`: 886/3, coverage 99.07%), then merged. `main`
  `23d43ae` → `f21033b`; test count 865 → 886.
- **2026-05-29** — ENH-#42 shipped (both halves): in-add-on network/IP editor (PR #48 at `16eda5e`) and add-on-language switcher (PR #49 at `3765862`). `installer.main()` gained "Network settings" + "Add-on language" entries; hidden `addon_language` setting; `i18n.supported_languages()` 7 → 12 plus `effective_language()` and a pinned-locale `L()` override.
- **2026-05-29** — ENH-#38 resolved: ruff enforced across the whole codebase (PR #50 at `092444a`). `ruff check .` + `ruff format --check .` clean (tests/ + tools/ included); config consolidated (ruff.toml authoritative + pyproject mirror, `C4` added); CI flipped to whole-tree. Filed ENH-#51 to track the mypy `--strict` source rollout (curated allowlist, leaf-first, source-only).
- **2026-05-29** — Configurator icon + bundling session (`area:configurator`). Generated the configurator's real app icon set from the repo-root add-on `icon.png` (256×256) via `tauri icon`, fixing a latent build-breaker (three `bundle.icon` files were missing on disk); pruned the mobile `ios/`/`android/` outputs and refreshed the icons README. First-pass `npm run tauri -- build` succeeded → MSI (3.0 MB) + NSIS setup (1.9 MB). Draft PR #52 (`claude/configurator-icon-bundle-h4n7k2p9`, tip `8cecd42`); `main` unchanged (configurator code lives under the PR). Software-verified only (build + bundle); installed-app/icon appearance not verified.
- **2026-05-29** — ENH-#51 mypy `--strict` rollout PR 1 (`area:addon`). Stood up an
  incremental strict gate instead of a global flip (source baseline **788 errors / 35
  modules** at py3.9): `mypy.ini` (authoritative) + `pyproject` mirror gain `strict`,
  `follow_imports = silent`, `python_version` 3.10 → 3.9, and a curated `files=`
  allowlist; `tools/type_check.py` gains a blocking `--gate` mode (default stays
  non-blocking) wired into a new CI `types` job. First 7-module leaf batch annotated to
  zero strict errors (signatures + stale-`# type: ignore` removal; no logic changes);
  `nas_playback_adapter` deferred (cascades into settings_reader/oppo_control). Guard
  tests (build-13, g6) updated in lockstep. Draft PR #53
  (`claude/enh51-mypy-strict-a7k3m2x9`, tip `62d811f`), all 9 CI checks green; `main`
  unchanged (work on the unmerged PR). Added memory `mypy-strict-gate-rollout`.
- **2026-05-29** — ENH-#51 mypy `--strict`: **merged PR 1** (PR #53) to `main` at
  `aa0cf68` (verified the combination — main's only advance since the PR base was
  docs-only; post-merge gate 933/3, coverage 99.10%, ruff + `mypy --gate` clean;
  branch purged) and **opened PR 2** (draft PR #54, `claude/enh51-mypy-pr2-k3n8m2q6`,
  tip `08a1b79`). PR 2 expands the gate `files=` allowlist **7 → 23**: 12 already-
  strict-clean modules locked in with zero code change (found via a full-tree
  landscape run) + 4 leaf modules annotated to zero strict errors (`arch_benchmark`,
  `diagnostic_logging`, `i18n`, `tv_control` — signatures + pinned locals, no logic
  changes). All CI green on #54. Established the **already-clean-lock-in** technique
  (memory `mypy-strict-gate-rollout` updated); next leaf groups are the `avr_*`
  type-fix backends, then a strategy for the `no-redef` import-fallback modules.
- **2026-05-29** — ENH-#51 PR 3 + **bulk-merge-all-pending**. (1) Shipped **PR 3**
  (the `avr_*` type-fix backends): annotated `avr_denon_marantz`/`avr_onkyo_eiscp`
  (socket `cast` to the `SocketLike` Protocol), `avr_yamaha`/`avr_sony_audio` (pin
  `urlopen().read()`; `cast` object-typed `int`/`list`/`map`/`meta.get` values),
  `avr_diagnostics` (`dict→dict` `@overload` on `sanitize_payload`; 2 stale ignores
  removed) → gate allowlist **23 → 28**, 34 strict errors cleared. Fixed a **latent
  Python 3.9 import bug**: `bytes | str` in the `HttpGet`/`SonyPost` module-level
  aliases is PEP-604 evaluated eagerly at import (not lazied by the `__future__`
  import) → `TypeError` on the 3.9 floor; → `typing.Union`. (2) On the operator's
  `merge all pending` directive, merged the whole open-PR queue to `main` in
  dependency order: **#54** (mypy PR 2) `56b7a17` → **#56** (mypy PR 3, recreated
  from auto-closed #55) `aa4143f` → **#52** (configurator icon) `859238e`. **Lesson:
  merging a PR with `--delete-branch` auto-CLOSES any PR stacked on that branch**
  (GitHub closes rather than retargets; a closed-with-deleted-base PR can't be
  reopened) — recreate it against `main`. `main` `aa0cf68` → `859238e`; post-merge
  gate **28/0**, `pytest -n auto` **933/3**, coverage **99%**. Memory
  `mypy-strict-gate-rollout` updated (PR 3 idioms + the stacking/verified-SHA
  lessons). All addon deliveries now merged; PR 4 = the `no-redef` import-fallback
  strategy (needs a design decision first).
- **2026-05-29** — ENH-#57 + README credits session (`area:addon`). Added a
  **change-scoped fast local test loop**: `tools/dev_test.py` wraps `pytest --testmon`
  so a local run executes only the tests affected by changed code (the full suite + 99%
  coverage gate stay the CI/`verify.sh`/pre-push backstop). Merged 4 PRs to `main`:
  [#59](https://github.com/skull-01/script.oppo203.iso.external/pull/59) `9f102a3`
  (the tool + `pytest-testmon` dev dep + `.testmondata` ignore + 5 guard tests; filed
  ENH-#57 to track it),
  [#58](https://github.com/skull-01/script.oppo203.iso.external/pull/58) `61999e3`
  (README **Credits** section),
  [#60](https://github.com/skull-01/script.oppo203.iso.external/pull/60) `343aff2`
  (Phase C checklist entry), and
  [#61](https://github.com/skull-01/script.oppo203.iso.external/pull/61) `2fdf869`.
  **CI lesson:** #59 reddened the **Python 3.9 compat-smoke** — `pytest-testmon` 2.2+
  dropped py3.9 but the add-on floor is 3.9, so `pip install -r requirements-dev.txt`
  failed there; repaired forward with an env marker (#61,
  `; python_version >= "3.10"`) and re-confirmed all six CI jobs green. Also found
  `tools/dev_build.py` is **not** on `main` (corrected the stale `dev-build-iteration-loop`
  memory) and that the `pre-push` hook runs the 99% coverage gate. `main` `859238e` →
  `2fdf869`; tests **933 → 938 passed, 3 skipped**, coverage **99.07%**, gate **28/0**.
- **2026-05-30** — ENH-#51 mypy `--strict` **PRs 4–7** (`area:addon`), completing the
  idiom + cascade scope the operator requested on `resume` ("do all of these" → "everything
  now"). Gate **28 → 46 modules** across four **stacked** draft PRs (merge #63→#64→#65→#66):
  **PR 4** [#63](https://github.com/skull-01/script.oppo203.iso.external/pull/63) `7568f89`
  (import-fallback leaf modules; settled the `no-redef` strategy = `# type: ignore[no-redef]`
  on the except-branch bare import only; `_FsLike` Protocol; `# type: ignore[attr-defined]`
  for hub re-exports); **PR 5** [#64](https://github.com/skull-01/script.oppo203.iso.external/pull/64)
  `8b06744` (the `settings_reader`+`oppo_control` hubs; `Settings.get`/`__getitem__` → `Any`;
  `HARDWARE_COMPAT` annotated to stop `object` inference); **PR 6**
  [#65](https://github.com/skull-01/script.oppo203.iso.external/pull/65) `8406b43` (the 7-module
  cascade group; nas_playback_adapter needed zero code change once the hubs were typed); **PR 7**
  [#66](https://github.com/skull-01/script.oppo203.iso.external/pull/66) `6fed436`
  (oppo_remote/external_player/installer/preset_manager). Annotations/casts/`# type: ignore`
  only — no behavior change; each verified `mypy --gate` 0 / `pytest -n auto` 938/3 /
  coverage ~99.05% / ruff clean. PRs 6–7's mechanical per-module annotation was **delegated to
  parallel general-purpose sub-agents** (one file each; `mypy --no-incremental` to avoid
  concurrent-cache corruption; cross-sibling no-untyped-call left for the combined gate), then
  verified on the main thread (gate + full suite + coverage + diff review). SHAs commented on
  #51; Phase-A entries per PR in the manual checklist. `main` unchanged (`c48bb43`) — all work
  on the unmerged PR branches. Memory `mypy-strict-gate-rollout` updated.

- **2026-05-30 (PM)** — ENH-#51 mypy `--strict` **rollout completed + full stack merged**
  (`area:addon`). On `resume` the operator picked ENH-#51 PR 8 and chose to base it on #66;
  built PR 8 ([#69](https://github.com/skull-01/script.oppo203.iso.external/pull/69) `fae98cb`)
  gating the last ungated source — `service.py` / `default.py` / `playercorefactory_merge`
  (gate 46→49, annotations/casts/`# type: ignore` only). Then on the operator's "merge
  everything", merged the whole stack to `main` in order: #63 `77305ee` → #64 `8dca608` →
  #65 `b636d30` → #66 `3f4d5cb` → #69 `4525d86` — **each child retargeted to `main` before its
  parent's branch was deleted**, avoiding the stacked-PR auto-close that bit #55. Post-merge
  `main` (`4525d86`) re-verified green: `mypy --gate` **49/0**, `pytest -n auto` 938/3, serial
  coverage 99.05%. Merge SHAs commented on #51 (stays open per the only-operator-closes norm).
  **ENH-#51 source rollout COMPLETE — every `resources/lib` module + top-level
  `service.py`/`default.py` is gated.** PR #68 (configurator wizard-state mapping) was left
  **open** — out of scope of the ENH-#51 merge, needs an in-area configurator session.
  **Tool-channel instability** recurred hard this session (Read / Grep / Bash+PowerShell stdout
  intermittently returned stale or fabricated content); mitigated by file-redirect readbacks,
  cross-channel checks, byte-validated Edits, and never reusing a pre-commit SHA. Memory
  `mypy-strict-gate-rollout` updated.
- **2026-05-30 (EOD — configurator review → fix → merge → close-out)** — Operator: `resume`
  → merged the two pending EOD docs (#70/#71, resolving a §3b add/add conflict by keeping #71's
  detailed §3b and folding in #70's `384d180` note) → `/code-review` of the wizard-wiring
  **PR #68** (filed 16 bugs **#72–#87**, `type:bug`/`area:configurator`) → "create a plan to
  close them all" → executed a 3-phase plan. **Phase 2:** fixed the 12 high/med bugs on the #68
  branch (commits `6d68206` Rust hardening / `7120439` config-write safety / `46d4ca8` IP-test +
  state) and **merged #68** (`454e5ab`). **Phase 3:** cleanup **PR #88** (`a4ad7ad`) —
  #85/#77/#86/#87 + ENH-#41 Part C (commits `d48b0c7`/`9acb6a1`/`384e3d4`; new `src/xml.ts` +
  `src/players.ts`). **Phase 4:** **PR #89** (`9401fb3`) — ENH-#44 hardware-validation
  solicitation (`docs/HARDWARE_VALIDATION.md` + README). All 18 issues SHA-commented + Phase-C
  checklist entries; none closed (operator's call). Configurator: 63 vitest + tsc/vite/cargo
  green; add-on 938/3, coverage 99.05%, mypy gate 49/0 unchanged. Recreated a wiped `.venv`
  mid-session (pre-push hook needs it). `main` `4525d86` → `9401fb3`. Key gotcha logged:
  PowerShell 5.1 splits native args containing `"` and mojibakes non-ASCII in inline scripts —
  use `--body-file` / Edit/Write for issue/PR/doc content, keep inline scripts ASCII.
- **2026-05-30 (evening — merge the PM-session PR stack + publish the first configurator
  binary)** — Operator: `resume` → picked **"merge all 6 green drafts."** Reviewed and merged
  the six PRs the 2026-05-30 PM session had left open as drafts (all base `main`, none stacked,
  all CI-green 8/8): **#93** `BUILD_PLAN.md` refresh (`6d657ea`), **#91** Chinoppo `M9205 V1`
  split (`36f9cbd`, `area:addon` — the only runtime code), **#94** configurator build recipe
  (`60f7897`), **#95** first-binary evidence (`4af93b5`), **#92** canonical Plan-format norm
  (`dce80cd`), and **#96** this handoff. `main` `0f9fd67` → `dce80cd` (+ the #96 merge).
  **Published `configurator-v0.1.0`** — flipped the PM session's draft GitHub release to a
  public **pre-release** (tag at `dce80cd`; MSI 3.15 MB + NSIS 2.05 MB + SHA-256 sidecars;
  unsigned, software-verified only; the add-on's v2.9.13 stays repo "Latest"). Re-verified the
  **combined** `main` green before publishing/finalizing: add-on `ruff` clean, `mypy --gate`
  **49/0**, `sync_version` 2.9.13, `pytest -n auto` **943/3**, serial coverage **99%**;
  configurator `tsc -b` + `vite build` clean, **vitest 64/64**; `main`@`dce80cd` CI green.
  Order discipline: confirmed **#94 ⊂ #95** (`merge-base --is-ancestor`) so #94→#95 merged
  clean; **#92 and #96 both touch this file**, so #96 was merged **last** and its branch was
  **reset to `main` + re-authored** to the merged reality (its original "5 open drafts, none
  merged" content was made false by this very session). **Both §3a and §3b rewritten** (session
  touched both areas); **§17a** #51→CLOSED + new #91 / v0.1.0-binary rows + "Last refreshed"
  bumped; **§19** updated. The agent closed no issues (operator closed #51); the M9205 split and
  the binary are PR-only themes (no SHA-comment target).

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

Last refreshed: **2026-05-30 (evening — PM-session 6-PR stack merged (#91–#96) + `configurator-v0.1.0` published; #51 closed by operator)**.

| # | Title | Area | Labels | State | Implementing SHA(s) | Operator-verified? |
|---|---|---|---|---|---|---|
| 22 | [Bug]: wizard launch failure (`No module named 'wizard'`) | addon | `bug`, `area:addon` | CLOSED 2026-05-28 | `b7471db` on `wip/wizard-ux` (wizard now removed entirely by `3abf486` on `claude/strip-wizard-g4feovqi`, merged via #40 at `59eb511`) | closed by operator |
| 38 | ENH-: clear ruff backlog on main (336 errors, 172 auto-fixable, 66% in 3 test files) | addon | `area:addon` | OPEN | **Resolved** by [PR #50](https://github.com/skull-01/script.oppo203.iso.external/pull/50) at `092444a` — `ruff check .` + `ruff format --check .` clean whole-codebase, enforced in CI | awaiting operator close |
| 41 | ENH-: configurator owns add-on configuration; add-on is read-mostly | addon | `area:addon` | OPEN | Part A `816bde2` (PR #45). Addon side of Parts B + C **merged** via [PR #46](https://github.com/skull-01/script.oppo203.iso.external/pull/46) at `f21033b`. **Configurator side of Part C done** via PR #88 (`d48b0c7`) — provenance marker written into the generated settings.xml. | Phase A/C queued; awaiting operator close |
| 42 | ENH-: minimal in-add-on settings menu (TV/OPPO/AVR/Kodi IPs + language) | addon | `area:addon` | OPEN | **Merged** via [PR #48](https://github.com/skull-01/script.oppo203.iso.external/pull/48) at `16eda5e` (network/IP editor) + [PR #49](https://github.com/skull-01/script.oppo203.iso.external/pull/49) at `3765862` (language switcher) | Phase A/C queued; awaiting operator close |
| 43 | ENH-: split `resources/lib` into TV / Oppo / AVR / Kodi sub-packages | addon | `area:addon` | OPEN | **Merged** via [PR #47](https://github.com/skull-01/script.oppo203.iso.external/pull/47) at `3ba5009` (impl `18a97a6` + test-isolation `69e32b3`) | Phase A queued |
| 44 | ENH-: hardware-validation testing — lending, donations, tester reports wanted | addon | `area:addon` | OPEN | **Solicitation merged** via [PR #89](https://github.com/skull-01/script.oppo203.iso.external/pull/89) at `9401fb3` — `docs/HARDWARE_VALIDATION.md` (per-family status matrix + how to help) + README pointer | awaiting operator (standing community call) |
| 51 | ENH-: roll out mypy --strict across add-on source (curated allowlist, leaf-first) | addon | `area:addon` | CLOSED 2026-05-30 | **ROLLOUT COMPLETE — all merged to `main` 2026-05-30 PM (gate→49).** PRs 1–3 (`aa0cf68`/`56b7a17`/`aa4143f`, →28), then PRs 4–8 merged in order: #63 `77305ee` (→33), #64 `8dca608` (→35), #65 `b636d30` (→42), #66 `3f4d5cb` (→46), #69 `4525d86` (service.py/default.py/playercorefactory_merge →49). Post-merge `main` green: gate 49/0, pytest 938/3, coverage 99.05%. | **closed by operator 2026-05-30** |
| 68 | configurator: wire the wizard to the add-on contract (slices 1–7) | configurator | _untracked theme (PR-only)_ | MERGED 2026-05-30 | [PR #68](https://github.com/skull-01/script.oppo203.iso.external/pull/68) at `454e5ab` — 7-slice wizard wiring; a /code-review filed 16 bugs (#72–#87), the 12 high/med fixed on-branch before merge (`6d68206`/`7120439`/`46d4ca8`) | software-verified; Phase C on-device queued |
| 52 | (no issue) configurator app icon + first MSI/NSIS bundle | configurator | _untracked theme_ | MERGED 2026-05-29 | [PR #52](https://github.com/skull-01/script.oppo203.iso.external/pull/52) at `859238e` — real icon set replaces the PR #35 stub; fixes a latent `bundle.icon` build-breaker; MSI 3.0 MB + NSIS 1.9 MB | Phase C on-device (install, confirm icon + launch) queued |
| 57 | ENH-: change-scoped fast local test loop (pytest-testmon) | addon | `area:addon` | OPEN | **Merged** via [PR #59](https://github.com/skull-01/script.oppo203.iso.external/pull/59) at `9f102a3` (`tools/dev_test.py` + `pytest-testmon` dev dep + 5 guard tests); py3.9-marker fix [PR #61](https://github.com/skull-01/script.oppo203.iso.external/pull/61) `2fdf869` | awaiting operator close (Phase C software check queued) |
| 72–87 | configurator PR #68 review bugs (config-write safety, ssh/probe/deploy hardening, IP-control test, persisted state, + cleanups) | configurator | `type:bug`, `area:configurator` | OPEN (16 issues) | Fixed across [PR #68](https://github.com/skull-01/script.oppo203.iso.external/pull/68) `454e5ab` (12 high/med — `6d68206`/`7120439`/`46d4ca8`) + [PR #88](https://github.com/skull-01/script.oppo203.iso.external/pull/88) `a4ad7ad` (5 cleanups + ENH-#41 Part C). SHA commented on each. | software-verified; Phase C on-device queued; awaiting operator close |
| 91 | (no issue) Chinoppo M9205 V1 split into a distinct hardware model | addon | _untracked theme (PR-only)_ | MERGED 2026-05-30 | [PR #91](https://github.com/skull-01/script.oppo203.iso.external/pull/91) at `36f9cbd` — new `chinoppo_m9205_v1` enum **appended** to settings.xml, mirrored through settings_reader/hardware_profiles/hardware_capabilities as an exact M9205 clone; configurator `players.ts` re-pointed; +5 tests, count guards 17→18 | software-verified; Phase A/C on-device queued |
| 94–95 | (no issue) configurator first Windows binary v0.1.0 (build recipe + evidence) | configurator | _untracked theme (PR-only)_ | MERGED + PUBLISHED 2026-05-30 | [PR #94](https://github.com/skull-01/script.oppo203.iso.external/pull/94) `60f7897` (build recipe: `BUILD.md`, `dist` alias, version guard) + [PR #95](https://github.com/skull-01/script.oppo203.iso.external/pull/95) `4af93b5` (evidence + notes); release **`configurator-v0.1.0`** published as a public pre-release (MSI + NSIS, unsigned) | Phase C on-device (install on clean machine, confirm launch) queued |
| 92–93 | (no issue) canonical Plan-format norm + BUILD_PLAN.md refresh | meta | _untracked theme (PR-only, docs)_ | MERGED 2026-05-30 | [PR #92](https://github.com/skull-01/script.oppo203.iso.external/pull/92) `dce80cd` (Plan-format norm in AGENTS.md + §1/§4 triggers + CLAUDE.md pointer) + [PR #93](https://github.com/skull-01/script.oppo203.iso.external/pull/93) `6d657ea` (BUILD_PLAN.md refresh) | docs-only; no verification needed |

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
- **2026-05-29 (spine-revision branch — EODs #2, #3)** — Parallel history on
  `docs/eod-handoff-2026-05-29-pm` (PR #37). Authored the §3a/§3b two-area
  restructure of §1, §2a, §3, AGENTS.md, `.claude/commands/resume.md`,
  `docs/ai-handoff/AI_RESUME_GUIDE.md` §9; ran one addon session under the new
  spine (audited `wip/wizard-ux` for v2.9.14, fixed a single ruff I001 in
  `tools/dev_build.py`, filed issue #38 for the 336-error ruff backlog).
  **Header "Last sync" on that branch was `394f9fc`** (the PR #30 merge); tests
  on `wip/wizard-ux` were 999 passed / 3 skipped / 99.10% coverage. The §3a/§3b
  content authored on that branch is preserved only via this entry — the actual
  §3a/§3b on `main` was overwritten by the PM bulk-merge entry below.
- **2026-05-29 (EOD — strip-wizard session)** — End-of-day after a single-theme
  addon session that stripped the in-Kodi setup wizard from the add-on. PR
  [#40](https://github.com/skull-01/script.oppo203.iso.external/pull/40) on
  `claude/strip-wizard-g4feovqi` (tip `92a9408`) was open as draft. 44 files
  changed, +313 / −5814. Tests: **865 passed, 3 skipped** in ~10s on the strip
  branch; coverage **99.05%** (≥ 99% floor). Filed 4 new `area:addon` ENH
  issues — #41 configurator-owns-config policy, #42 in-add-on settings menu,
  #43 module split (TV/Oppo/AVR/Kodi), #44 hardware-testing solicitation.
  Created [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) on `main` (commit
  `3967cb6`) with the strategic direction + open-issue grid + suggested
  ordering. Header "Last sync" updated from `4e54c5d` to `3967cb6`; tests on
  `main` re-confirmed at **987 passed, 3 skipped** in ~12s. §3 rewritten to
  record the strip-wizard PR + new issues; §17a backlog cache populated for
  the first time (with Area column added) — six rows: #22 (closed), #38, #41,
  #42, #43, #44.
- **2026-05-29 (EOD — config-owner-policy session)** — Second `done for
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
  **987 passed, 3 skipped** in 10.69s; coverage **99.08%**. SHA `1ed15a3`
  commented on issue #41 per the only-operator-closes-issues norm. Parts B + C
  of #41 deferred to the next session — both touch `resources/settings.xml`,
  which PR #40 also modifies.
- **2026-05-29 (PM — bulk-merge session)** — Operator typed `resume` then
  directed "merge all pending, operator will skip review." Bulk-merged the
  five mergeable PRs in dependency order:
  [#40](https://github.com/skull-01/script.oppo203.iso.external/pull/40)
  strip-wizard at `59eb511`,
  [#45](https://github.com/skull-01/script.oppo203.iso.external/pull/45)
  config-owner-policy Part A at `816bde2` (after resolving a
  `docs/MANUAL_VERIFICATION_CHECKLIST.md` conflict that preserved both #40 and
  #45 Phase A entries),
  [#33](https://github.com/skull-01/script.oppo203.iso.external/pull/33)
  window-control IPC at `45c6572`,
  [#34](https://github.com/skull-01/script.oppo203.iso.external/pull/34) state
  persistence at `bc60074`,
  [#35](https://github.com/skull-01/script.oppo203.iso.external/pull/35) cargo
  unblock at `12e5b18`. Closed three superseded/stale PRs without merge:
  [#39](https://github.com/skull-01/script.oppo203.iso.external/pull/39)
  (wip/wizard-ux — predecessor of #40),
  [#36](https://github.com/skull-01/script.oppo203.iso.external/pull/36) (stale
  mid-day handoff),
  [#32](https://github.com/skull-01/script.oppo203.iso.external/pull/32) (stale
  §3 refresh + ruff-target line now in tension with #38). Resolved this PR
  ([#37](https://github.com/skull-01/script.oppo203.iso.external/pull/37) the
  two-area spine revision) against the new `main`: took #37's structural
  changes (§1 step 2 multi-area wording, §2a's 14-row table with `auto-repo` /
  `auto-system` / `manual` tiers, §3a/§3b split, AGENTS.md area-label rule,
  `.claude/commands/resume.md` two-area procedure, AI_RESUME_GUIDE.md §9
  update); took `main`'s §17a (6 rows); rewrote §3b to record the four
  configurator-area PR outcomes this session; **§3a still carries the stale
  wip/wizard-ux v2.9.14 content from #37 and will be overwritten by the next
  EOD**. `pytest -n auto --basetemp=build\_pt` on `main` after the five
  merges: **865 passed, 3 skipped in 10.40s** (test count dropped from 987 →
  865 because #40 deleted the wizard test files; coverage **99.05%** ≥ 99%
  floor). Phase A on-device verification of #40 was **NOT** performed —
  operator chose to defer per the skip-review directive; revert remains
  available if hardware testing later flags an issue. No `area:configurator`
  labels back-applied to any prior items in this session.
- **2026-05-29 (EOD — `done for the day` after PM bulk-merge)** — Doc-only
  refresh. Header "Last sync" updated from `7b65ed2` to `bc79649` (PR #37
  merge); test count updated from 987 → **865 passed, 3 skipped** to reflect
  the wizard test files deleted by #40 (coverage **99.05%** on the lower
  denominator). **§3a rewritten** to drop #37's stale wip/wizard-ux v2.9.14
  content (replaced by main's current addon state: PR #40 + #45 shipped, #41
  Parts B + C unblocked, five open addon issues #38/#41/#42/#43/#44, candidate
  themes refreshed). **§3b dedeuplicated** (two "As of" headers merged into
  one, no content change beyond noting the `configurator-icon-files-missing`
  memory was pruned this EOD and adding a fourth candidate theme for the
  configurator-side ENH-#41 Part C). **§2a parenthetical** updated to note PR
  #35 satisfied row 13 (icon stub). **Memory pruned:** deleted
  `configurator-icon-files-missing.md` (carved out by PR #35); MEMORY.md index
  updated. **No new code commits, no new issues, no new branches.** Tree
  clean; `pytest -n auto --basetemp=build\_pt` on `main` re-confirmed at 865
  passed / 3 skipped / 9.95s.
- **2026-05-29 (EOD — ENH-#41 Parts B + C addon session)** — Single-theme
  addon session that implemented the addon-side of
  [ENH-#41](https://github.com/skull-01/script.oppo203.iso.external/issues/41)
  Parts B (in-add-on guidance hint) and C (configurator-managed-key
  overwrite warning). PR
  [#46](https://github.com/skull-01/script.oppo203.iso.external/pull/46) on
  `claude/enh41-bc-config-hint-a4n9k2m` (tip `3ccd9f1`) opened as draft. 17
  files changed, +697 / -3:
  [`service.py`](service.py) gained the `CONFIGURATOR_MANAGED_KEYS`
  constant (42 keys), `_snapshot_managed_settings` /
  `_changed_managed_keys` / `_resolve_localized` /
  `_notify_config_hint_once_per_session` /
  `_warn_overwritten_managed_keys` helpers, and a new `Monitor.__init__`
  + `Monitor.onSettingsChanged` that fires Part B's once-per-session
  toast and Part C's per-key warning (the class docstring records the
  no-state-mutation invariant preserved from PR #40);
  [`resources/settings.xml`](resources/settings.xml) gained one `<setting
  id="config_owner_hint" label="30290" type="lsep"/>` at the top of
  `<category id="connection">` (`tests/test_all.py` settings-count
  assertion bumped 97 → 98); 12 PO files gained four new strings (#30290
  banner, #30291 notification body, #30292 per-key warning template with
  `{key}` placeholder, #30293 notification title — non-en_gb files use
  msgid=msgstr fallback per convention);
  [`tests/test_v2914_build1_config_owner_hint.py`](tests/test_v2914_build1_config_owner_hint.py)
  is new with 21 tests across 5 classes (`TManagedKeysContent`,
  `TSnapshotAndDiff`, `TNotificationHelpers`, `TMonitor`,
  `TSettingsXmlAndPo`);
  [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](docs/MANUAL_VERIFICATION_CHECKLIST.md)
  gained a Phase A entry with a six-step Phase C on-device verification
  script for #46. Tests on the work branch: **886 passed, 3 skipped** in
  ~9.5s (the +21 over `main`'s 865 are this PR's new tests); ruff clean
  on touched Python files (257 pre-existing repo-wide errors covered by
  [ENH-#38](https://github.com/skull-01/script.oppo203.iso.external/issues/38)).
  SHA `3ccd9f1` commented on issue #41 per the only-operator-closes
  norm. Kodi-API caveat documented in the PR body: there is no "settings
  dialog opened" event; Part B's "first-open" notification is
  implemented as "first **change** per session", with the always-visible
  lsep banner as the on-open counterpart. **§3a rewritten** to record
  open draft PR #46, what's done, what's left, and refreshed candidate
  themes. **§3b not touched** (no configurator work this session).
  **§17a row for #41 updated** to record the Parts B + C SHA on draft
  PR #46 (configurator side of Part C still pending). **Header
  unchanged** — "Last sync" stays at `bc79649` and tests-on-`main` at
  865/3/99.05% because `main` had no operational changes this session.
  Phase A on-device verification of #46 deferred to next session; Phase
  A of #40 still deferred from PM bulk-merge.
- **2026-05-29 (EOD — ENH-#43 lib sub-package split session)** — Two-part
  addon session. (1) **Drove PR #46 to green:** the ENH-#41 B+C PR's "Lint and
  format checks" CI job was failing on a `ruff format` diff in `service.py`'s
  `CONFIGURATOR_MANAGED_KEYS` tuple (the PR's local gate had run `ruff check`
  but not `ruff format --check`); committed `52f1cd7` to fix it — all 7 PR
  checks now green and mergeable. (2) **Implemented ENH-#43** on draft
  [PR #47](https://github.com/skull-01/script.oppo203.iso.external/pull/47)
  (`claude/enh43-lib-subpackages-r9k2m4x7`, tip `69e32b3`): moved all 46
  `resources/lib` modules into `tv/`/`oppo/`/`avr/`/`kodi/` (incl. `version.py`
  → `kodi/`); added a lazy `sys.meta_path` alias finder in
  `resources/lib/__init__.py` so legacy flat names (`resources.lib.X` + bare
  `X`) resolve to the same canonical objects; made module-top cross-family
  imports explicit while keeping lazy in-function imports bare; updated the
  `version.py` importers in `sync_version.py` (project-root sentinel),
  `package.yml`, `package_release.sh`, `verify.sh`, `audit_release.py`; updated
  ~70 flat-path test literals + the kodi-stub contexts (new
  `tests/_support/lib_buckets.py`) + new `tests/__init__.py` for the
  unittest-discover path; pragma'd 12 now-dead bare-name fallback branches;
  added a per-test isolation fixture (`69e32b3`) to remove `-n auto` flakiness
  the move exposed. Gates: `pytest -n auto` 865/3 (green across repeats),
  serial coverage **99.07%**, ruff check+format clean, `unittest discover`
  484 OK, `audit_release` 580/580, runtime ZIP 70 files (50 bucketed). SHA
  `18a97a6` commented on issue #43. **§3a rewritten** to record both in-flight
  PRs (#46 + #47); **§3b untouched** (no configurator work). **§15** gained an
  ENH-#43 journey bullet; **§17a** #43 row + #41 tip + "Last refreshed"
  updated. **Header unchanged** — `main` had no operational changes this
  session (ENH-#43 lives on the branch / PR #47, not merged). Software-verified
  only; Phase A + Phase C steps for #47 queued in the manual checklist.
- **2026-05-29 (EOD — PR #47 + #46 merge session)** — Addon session that drove
  the two in-flight draft PRs to merge. Reviewed both; found the prior §3a
  "disjoint files" claim was wrong (they overlap on `service.py` /
  `tests/test_all.py` / `docs/MANUAL_VERIFICATION_CHECKLIST.md`). Merged **PR #47**
  (ENH-#43 lib split) at `3ba5009`; then integrated the new `main` into **PR #46**'s
  branch locally (clean auto-merge), ran the **full gate on the combined tree**
  (commit `126bac9`: `pytest -n auto` 886/3, serial coverage 99.07%, ruff clean,
  `unittest discover` 505 OK, `audit_release` 580/580, doc/version/i18n/layout
  `--check` OK), pushed (pre-push hook re-ran the coverage gate), waited for CI
  green, then merged **PR #46** (ENH-#41 Parts B+C) at `f21033b`. Both
  `claude/enh4*` branches deleted. Merge SHAs commented on issues #43 and #41
  (left open for operator). **§3a rewritten** to the merged state + a "verify the
  combination, not two green CIs" lesson; **§3b untouched** (no configurator
  work). **§15** gained a merge bullet; **§17a** rows #41/#43 + "Last refreshed"
  updated. **Header** "Last sync" `bc79649` → `f21033b`, tests `865` → **886
  passed, 3 skipped**, coverage `99.05%` → **99.07%**. No new issues/branches;
  ENH-#42 now unblocked by #43's bucket layout. Phase A/C on-device verification
  of #40/#46/#47 still deferred.
- **2026-05-29 (EOD — ENH-#42 + ruff-enforcement session)** — Operator-driven session. (1) Landed the finished ENH-#42 PRs to `main`: #48 network/IP editor at `16eda5e`, #49 language switcher at `3765862` (retargeted #49 to `main` before deleting #48's branch to avoid stacked-PR auto-close). (2) ENH-#38 ruff backlog **resolved** via PR #50 at `092444a` — `ruff check .` + `ruff format --check .` clean across tests/tools, consolidated config (ruff.toml authoritative + pyproject mirror + `C4`), CI flipped to whole-tree; 246 findings cleared, no source touched. Filed **ENH-#51** to track the mypy `--strict` rollout (source-only, curated allowlist, leaf-first) — Phase 2, not started. **§3a rewritten** to the merged state + the in-flight #51 plan; **§3b untouched**. **§15** gained two journey bullets; **§17a** rows #38/#42 + new #51 row + "Last refreshed" updated. **Header** "Last sync" `f21033b` → `092444a`, tests `886` → **932 passed, 3 skipped**, coverage `99.07%` → **99.10%**.
- **2026-05-29 (EOD — configurator icon + bundling session)** — Single-theme `area:configurator` session (`resume` → operator picked "icon + bundling"). Generated the real app icon set from the add-on artwork via `npm run tauri -- icon ..\icon.png` (replacing the PR #35 stub), pruned the `ios/`/`android/` outputs, refreshed `src-tauri/icons/README.md`, and produced the first Windows installers via `npm run tauri -- build` (MSI 3.0 MB + NSIS 1.9 MB, exit 0, ~1m13s). Two commits on `claude/configurator-icon-bundle-h4n7k2p9`: `eb9f1cf` (icon set) + `8cecd42` (Phase A/C checklist entry); draft **PR #52** opened. **§3b rewritten** to the in-flight #52 state + refreshed candidate themes (purpose-built icon now leads); **§3a untouched** (no addon work). **§15** gained a journey bullet. **§17a untouched** — no issues opened/closed/retitled (this theme has no tracked issue). **Header unchanged** — `main` had no operational changes (configurator code lives under unmerged PR #52); tests on `main` stay 932/3/99.10%. Added memory `configurator-tauri-build-recipe`. Suite re-confirmed green this session: 932 passed, 3 skipped.
- **2026-05-29 (EOD — ENH-#51 mypy --strict PR 1 session)** — Single-theme `area:addon` session (`resume` → operator picked ENH-#51). Shipped **PR 1** of the mypy `--strict` rollout to draft [PR #53](https://github.com/skull-01/script.oppo203.iso.external/pull/53) (`62d811f`): an incremental strict gate (`files=` allowlist + `follow_imports = silent` + `tools/type_check.py --gate` + new CI `types` job), `python_version` 3.10 → 3.9, the now-unused `[mypy-tests.*]` override dropped, and the first 7-module leaf batch annotated to zero strict errors (no logic changes; `nas_playback_adapter` deferred — cascades into settings_reader/oppo_control). Guard tests **build-13** (config shape) and **g6** (CI `types` job + gate command) updated in lockstep; SHA `62d811f` commented on #51; Phase A entry added to `docs/MANUAL_VERIFICATION_CHECKLIST.md`. **§3a rewritten** to the in-flight PR #53 state + refreshed candidate themes (PR 2 leads); **§3b untouched** (no configurator work). **§15** gained a journey bullet; **§17a** #51 row + "Last refreshed" updated. **Header unchanged** — `main` had no operational changes (ENH-#51 lives on unmerged PR #53); tests on `main` stay 932/3/99.10%. Added memory `mypy-strict-gate-rollout`. All 9 PR #53 CI checks green; software-verified only, hardware validation not claimed.
- **2026-05-29 (EOD — ENH-#51 mypy --strict PR 1 merge + PR 2 session)** — `resume` → operator picked addon, then drove the ENH-#51 rollout across two PRs (within §4's 4-PR cap). (1) **Merged PR 1**: drove draft [PR #53](https://github.com/skull-01/script.oppo203.iso.external/pull/53) to `main` at `aa0cf68` — verified the combination first (main's only advance since the PR base was docs-only), marked ready, merged with `--delete-branch`, post-merge gate green (933/3, coverage 99.10%, ruff + `mypy --gate` clean), and fixed a dangling checklist `Implementing SHA` ref to the merged commit (`3e79ec6` on `main`). (2) **Opened PR 2**: draft [PR #54](https://github.com/skull-01/script.oppo203.iso.external/pull/54) (`claude/enh51-mypy-pr2-k3n8m2q6`, tip `08a1b79`, impl `92f2373`) expanding the gate `files=` allowlist **7 → 23** — 12 already-strict-clean modules locked in with zero code change (found via a full-tree landscape run) + 4 leaf modules annotated to zero strict errors (`arch_benchmark`, `diagnostic_logging`, `i18n`, `tv_control`; signatures + pinned locals, no logic changes). All CI green on #54 (Release + Type gate + compat 3.9/3.10/3.12 + lint + build ZIP + claude-review). **§3a rewritten** to the merged-PR-1 + in-flight-PR-2 state with PR-3 themes (the `avr_*` type-fix backends lead); **§3b untouched** (no configurator work). **§15** gained a journey bullet; **§17a** #51 row + "Last refreshed" updated. **Header** "Last sync" `092444a` → `aa0cf68`, tests `932` → **933 passed, 3 skipped** (coverage 99.10%). Memory `mypy-strict-gate-rollout` updated with the already-clean-lock-in technique. #51 stays open (multi-PR rollout); PR #54 awaiting operator review/merge.
- **2026-05-29 (EOD — ENH-#51 PR 3 + bulk-merge-all-pending session)** — `resume` → operator picked addon ENH-#51 PR 3, then said `merge all pending`. (1) **Shipped PR 3** (the `avr_*` type-fix backends): annotated the five remaining AVR backends to zero strict errors (allowlist 23 → 28, 34 errors cleared — socket `cast` to `SocketLike`, pinned `urlopen().read()`, `cast` object-typed `int`/`list`/`map`/`meta.get` values, a `dict→dict` `@overload` on `avr_diagnostics.sanitize_payload`, 2 stale `# type: ignore` removed) and fixed a **latent Python 3.9 import bug** (`bytes | str` module-level aliases evaluate eagerly at import → `TypeError` on 3.9; → `typing.Union`). (2) **Merged the whole open-PR queue** in dependency order: **#54** mypy PR 2 → `56b7a17`, **#56** mypy PR 3 (recreated from #55, which auto-closed when #54's base branch was deleted) → `aa4143f`, **#52** configurator icon → `859238e`; all branches purged. **Both §3a and §3b rewritten** to the merged state (this session touched both areas). **§15** gained a journey bullet (incl. the stacked-PR-auto-close lesson); **§17a** #41/#51 rows updated + new #52 row + "Last refreshed". **Header** "Last sync" `aa0cf68` → `859238e` (tests stay **933/3**, coverage 99%, gate **28/0**). Memory `mypy-strict-gate-rollout` updated (PR 3 idioms + stacking/verified-SHA process lessons). **Mid-session correction:** an issue-comment draft used a SHA predicted before committing (`ce97c69`); the content-integrity classifier correctly blocked it; re-posted with the real SHA `d36e76f` — nothing fabricated reached the repo or GitHub. All addon deliveries now merged; next is ENH-#51 PR 4 (the `no-redef` import-fallback strategy — needs a design decision first).
- **2026-05-29 (EOD — ENH-#57 fast-test-loop + README credits session)** — `resume` → operator picked an ENH-#43 follow-up, which they redefined as **change-scoped local testing** and (via the popup decision model) scoped to **pytest-testmon, local build loop only**. Built `tools/dev_test.py` (wraps `pytest --testmon` — only tests affected by changed code run) + `pytest-testmon` dev dep + `.testmondata` ignore + 5 guard tests; filed **ENH-#57** and merged it as [PR #59](https://github.com/skull-01/script.oppo203.iso.external/pull/59) `9f102a3`. Also merged the **README Credits** section ([PR #58](https://github.com/skull-01/script.oppo203.iso.external/pull/58) `61999e3`; Moremodey1 → AVForums per operator), a Phase C checklist entry ([PR #60](https://github.com/skull-01/script.oppo203.iso.external/pull/60) `343aff2`), and a **py3.9 fix** ([PR #61](https://github.com/skull-01/script.oppo203.iso.external/pull/61) `2fdf869`) after #59 reddened the 3.9 compat-smoke (testmon 2.2+ needs py≥3.10; gated the dev dep with a `; python_version >= "3.10"` marker). **§3a rewritten** to the merged state + the CI lesson; **§3b untouched** (no configurator work). **§15** gained a journey bullet; **§17a** new #57 row + "Last refreshed" updated. **Header** "Last sync" `859238e` → `2fdf869`, tests **933 → 938 passed, 3 skipped**, coverage **99.07%**, gate 28/0; full CI green on `main` (six jobs, verified). Memory `dev-build-iteration-loop` corrected (dev_build.py not on main; pre-push hook = coverage gate; dev-dep 3.9-marker rule). **Process note:** #59 was merged before CI finished, on local-3.12 evidence — the 3.9 matrix was the gap; **wait for CI green before merging dependency changes.** This EOD doc pushed via a doc-only PR (direct-to-`main` push is harness-blocked).
- **2026-05-30 (EOD — ENH-#51 mypy --strict PRs 4–7)** — `resume` → operator picked ENH-#51,
  said "do all of these" (the no-redef idiom modules + the cascade group), then chose
  **"everything now (PR 6+7)"** at the mid-session checkpoint. Shipped the whole idiom +
  cascade scope as **four stacked draft PRs** (gate **28 → 46 modules**): #63 (leaves) → #64
  (hubs) → #65 (cascade) → #66 (idiom modules); merge in that order. Annotations-only; each
  green locally (`mypy --gate` 0, `pytest -n auto` 938/3, coverage 99.04–99.05%, ruff clean).
  PRs 6–7 delegated to parallel sub-agents (`--no-incremental` to avoid mypy-cache races),
  verified by the combined gate + full suite + diff review. **§3a rewritten** to the 4-draft
  state + the merge-order resume steps + optional-PR-8 themes; **§3b untouched** (no
  configurator work). **§15** gained a journey bullet; **§17a** #51 row + "Last refreshed"
  updated. **Header** "Last sync" `2fdf869` → `c48bb43` (main carries the prior EOD PR #62;
  this session's ENH-#51 work is on the unmerged PRs, so main's gate stays **28/0** and tests
  **938/3**). Memory `mypy-strict-gate-rollout` updated (PRs 4–7 + the parallel-sub-agent
  technique). **§21** gained the scope-decision Q&A. This EOD doc pushed via a doc-only PR
  (direct-to-`main` push is harness-blocked).
- **2026-05-30 (PM EOD — ENH-#51 stack merge + done-for-the-day)** — Operator: "merge
  everything and done for the day." Merged the ENH-#51 stack #63→#64→#65→#66→#69 to `main`
  (tip `4525d86`), retargeting each child to `main` first to avoid the stacked-PR auto-close;
  left configurator PR #68 open (out of scope). Post-merge `main` re-verified (gate 49/0,
  938/3, coverage 99.05%); merge SHAs commented on #51. **Header** "Last sync" `c48bb43` →
  `4525d86`, gate **28 → 49**, coverage 99.07% → 99.05%. **§3a** rewritten to the
  completed-and-merged state; **§3b** gained a PM note (open PR #68 + the operator `384d180`
  upload of `configurator/CONFIGURATOR_HANDOFF.md` + installer zip); **§17a** #51 row →
  COMPLETE/merged, new #68 row, "Last refreshed" bumped; **§15** gained a merge-session bullet.
  This doc pushed via a doc-only PR (direct-to-`main` push is harness-blocked).
- **2026-05-30 (EOD — configurator review/fix/merge + done-for-the-day)** — After merging the
  two pending EOD docs (#70/#71), ran `/code-review` on PR #68 (filed #72–#87), then executed a
  3-phase close-out: fixed the 12 high/med bugs on the #68 branch and merged #68 (`454e5ab`);
  cleanup PR #88 (`a4ad7ad`, #85/#77/#86/#87 + ENH-#41 Part C); doc PR #89 (`9401fb3`, ENH-#44).
  **Header** "Last sync" `4525d86` → `9401fb3` + configurator-hardening summary + a 63-vitest
  line. **§3a** reframed to this configurator-led EOD (addon touches = #44 + #41 Part C; mypy
  still complete). **§3b** rewritten — #68 merged + hardened, #88 cleanup, no configurator work
  in flight, the 16 review bugs listed as open-awaiting-close. **§15** gained a
  review→fix→merge entry; **§17a** #68 → MERGED, new #72–#87 row, #41/#44 rows updated, "Last
  refreshed" bumped. All 18 issues SHA-commented (none closed — operator's call). Doc pushed via
  a doc-only PR (direct-to-`main` push is harness-blocked).
- **2026-05-30 (norm addition — canonical plan format)** — Operator: "every time I ask for
  a plan, follow this level of detail/quality/output", citing an example multi-PR plan from
  another repo. Distilled it (adapted to this repo's gates) into a new **`## Plan format`**
  section in [`AGENTS.md`](AGENTS.md) (ground-first → theme → per-PR scope blocks →
  dependency chain → 📊 rollup → ⚠️ risk callouts → verification regime → ✅/🛑/🔁), plus a
  §1 trigger row + a §4 build-norm bullet here and a `plan` / `scope this` entry in the
  `CLAUDE.md` trigger-vocabulary pointer. Docs-only; no code touched. Shipped via a doc-only
  PR (direct-to-`main` push is harness-blocked).
- **2026-05-30 (evening — merge the PM-session 6-PR stack + publish v0.1.0 + this handoff
  refresh)** — Operator: `resume` → **"merge all 6 green drafts."** Merged #93/#91/#94/#95/#92
  to `main` (`0f9fd67` → `dce80cd`), published `configurator-v0.1.0` as a public pre-release,
  and landed this doc as **#96**. To keep this file honest, **#96's branch was reset to `main`
  and re-authored** — its original PM-session content described #91–#95 as "open drafts," which
  this session merged. **Header** "Last sync" `9401fb3` → `dce80cd` + the merge/release summary,
  tests `938/3` → **943/3**, vitest `63` → **64**, ENH-#51 marked CLOSED. **§3a** rewritten
  (M9205 V1 split merged; #51 closed; long ENH-#51 history condensed — full detail stays in
  §15). **§3b** rewritten (v0.1.0 binary published; M9205 follow-up resolved). **§15** gained a
  merge/release journey bullet. **§17a** #51 → CLOSED, three new rows (#91, #94–95 binary,
  #92–93 docs), "Last refreshed" bumped. Combined `main` re-verified green (943/3, coverage 99%,
  mypy 49/0, ruff clean; configurator tsc/vite + vitest 64; `main`@`dce80cd` CI green). No new
  issues/branches; the agent closed nothing (operator closed #51). This doc pushed via PR #96
  (direct-to-`main` push is harness-blocked).

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

### 2026-05-29 — Merge order + stacked-PR auto-close (the `merge all pending` directive)

- **Q:** With three open PRs (#52 configurator, #54 mypy PR 2, #55 mypy PR 3 stacked
  on #54), what order merges safely?
  **A:** Stacking dictates it: **#54 → #55 → #52.** #55's base branch *is* #54's
  branch, so #54 must land first. #52 is independent (configurator-only) and goes
  last. Verified each was MERGEABLE/CLEAN and CI-green before merging.
- **Q:** What happened to #55?
  **A:** Merging #54 with `--delete-branch` deleted the branch #55 was based on, which
  **auto-closed #55** — GitHub *closes* (does not retarget) a PR whose base branch is
  removed, and a closed PR whose base is gone can't be reopened or retargeted. The
  fix: recreate the identical branch/commits as a new PR (**#56**) against `main` and
  merge that. Confirmed via `git merge-tree` it was 0-conflict and did **not** revert
  `main`'s newer `AI_RESUME_HANDOFF.md` (pr3 never touched that file, so the 3-way
  merge keeps main's copy). **General rule for stacks:** retarget the child PR to
  `main` *before* deleting the parent's branch, or expect the recreate dance.

### 2026-05-30 — ENH-#51 rollout scope ("do all of these" → how far in one session)

- **Q:** On `resume` the operator picked **both** ENH-#51 candidate themes at once — "PR 4
  (import-fallback strategy for the no-redef idiom modules)" **and** "the cascade group" —
  with "do all of these". One theme or many PRs?
  **A:** One theme (ENH-#51), delivered as a stack. The cascade group is blocked on the two
  un-migrated hubs (`settings_reader` 72 + `oppo_control` 111 errors), so the real sequence is
  PR 4 (leaves) → PR 5 (hubs) → PR 6 (cascade) → PR 7 (the larger hub-dependent idiom modules
  oppo_remote/external_player/installer/preset_manager). Four PRs — at §4's soft cap.
- **Q:** After PRs 4+5 (the hubs unblock everything), the remaining work was ~425 strict
  errors / 11 modules — larger than the two bullets implied. Continue now or checkpoint?
  **A:** Operator chose **"everything now (PR 6 + 7)"** (popup). Proceeded; parallelized the
  mechanical per-module annotation across general-purpose sub-agents to fit it in one session
  while keeping verification (gate + full suite + coverage + diff review) on the main thread.
