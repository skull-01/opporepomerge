# AI_RESUME_HANDOFF.md — session continuity for `script.oppo203.iso.external`

**Repo:** `github.com/skull-01/script.oppo203.iso.external` · **Default branch:** `main`
**Last sync ≈ commit `d6e3470`** (origin/main) · **Tests on `main`: 975 passed, 3 skipped**
**Latest release:** v2.9.13 · **Issue tracker:** GitHub **Pull Requests** (no GitHub Issues are used)

> This is the session-continuity entry point. Read it first when starting or resuming.
> Treat live code + `git`/`gh` output as authoritative; this file is the map and the memory.
> A deeper companion (build norms, architecture, full history) lives at
> [`docs/ai-handoff/AI_RESUME_GUIDE.md`](docs/ai-handoff/AI_RESUME_GUIDE.md).

---

## Commands this repo understands

These are natural-language triggers any agent must honor (also wired in `AGENTS.md` /
`CLAUDE.md`). Slash-command equivalents exist: `/resume`, `/done-for-the-day`, `/release`.

### `resume`
When the maintainer types **`resume`** (alone):
1. Read this doc (especially **Work in progress** below) and the repo instruction files
   (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`).
2. **Environment preflight** — run the **readiness checklist** in §2 so the machine can
   actually build/test the app. Print a small readiness table, then:
   - all rows green → one line `Environment: ready ✓` and continue;
   - an *auto* row (`.venv` / dev deps / paramiko) missing → **install it** (idempotent:
     `python -m venv .venv` if absent, then
     `.venv\Scripts\python.exe -m pip install -r requirements-dev.txt paramiko`), re-check,
     and report what was installed;
   - a *manual* row (Python, git, gh auth) missing → print the exact fix command and **STOP**
     for the maintainer (do not auto-install system/auth changes).
3. Report the **last 5 PRs created** and the **last 5 PRs completed (merged)** — this repo
   tracks work as PRs, not Issues:
   - created:  `gh pr list --state all --limit 5 --json number,title,state,createdAt`
   - completed: `gh pr list --state merged --limit 5 --json number,title,mergedAt`
   - (If GitHub Issues are ever adopted, also run `gh issue list --state all --limit 5`.)
4. Suggest what to work on next: if **Work in progress** has an unfinished task, list it
   **first** as the priority, then 1–2 more from **Open issues & next steps**, each with a
   one-line rationale.
5. **STOP and wait** for the maintainer to choose. Keep it concise.

### `done for the day`
When the maintainer types **`done for the day`**:
1. **Push ALL current work** — nothing stays only on this machine. On the current branch:
   `git add -A` (exclude `.claude/settings.local.json`), run the test command (below),
   then commit — a normal message if finished and green, or a `wip:` checkpoint commit
   (state what's unfinished + the test status) if not — then `git push`.
2. **Overwrite "Work in progress"** below with: date, current commit, task in flight,
   what's done, what's left, key files, related PR/branch, tests pass? (or "None — clean
   stopping point").
3. **Run the maintenance recipe** ("How to update this document") to refresh the volatile
   sections (journey, tracker state, tests, header "last sync ≈ commit").
4. **Commit & push the updated doc.** The doc lives on `main`; if you are on a feature
   branch, your work was already committed in step 1, so it is safe to update the doc on
   `main`: `git stash -u` (only if needed), `git checkout main && git pull`, edit, commit,
   push, then `git checkout -` to return. (If a quick PR is required by branch protection,
   open one for the doc-only change.)
5. Reply with an **end-of-day summary**. Do **NOT** start new feature work.

### `update AI_RESUME_HANDOFF.md`
Run the deterministic **maintenance recipe** at the bottom of this file to refresh the
volatile sections from git/PRs/tests.

---

## Work in progress (resume here first)

- **Date:** 2026-05-23 · **On:** `main` @ `d6e3470` · **Tests:** pass (975 passed, 3 skipped).
- **Status:** Clean stopping point. The session-continuity system (this doc, `AGENTS.md`,
  `CLAUDE.md`, `/resume` + `/done-for-the-day`) was set up and merged (PR #14). Nothing is
  left only on this machine.
- **In flight (next feature to ship):** branch **`wip/wizard-ux`** (pushed —
  `origin/wip/wizard-ux`) is the **v2.9.14 candidate** — five on-device wizard fixes + the
  dev-iteration tooling, all committed and green (981 passed, 3 skipped on that branch).
  **Not yet version-bumped or released.**
- **What's done there:** wizard launch fix (`No module named 'wizard'`), PO header fix for
  all 12 locales, "Setup files saved" location dialog, opt-in auto-install into Kodi
  (merge + backup), expanded player presets (M9205 V1 etc.), `tools/dev_build.py`.
- **What's left:** confirm on-device UX is final, then **`/release` v2.9.14** (full bump +
  evidence + tag + styled notes). It DOES change runtime behavior (wizard now launches +
  can install files) — say so in the "Runtime behavior" section of the notes.
- **Key files:** `resources/lib/wizard.py`, `resources/lib/installer.py`,
  `resources/lib/hardware_presets.py`, `resources/language/*/strings.po`,
  `tools/dev_build.py`.
- **Related:** branch `wip/wizard-ux` (no PR opened yet).

---

## Table of contents
1. Project overview
2. Environment & setup
3. How to run / test / validate (exact commands)
4. Build norms
5. Documentation & workflow conventions
6. Architecture / module map
7. Data model & config schema
8. Key flows / pipelines
9. Entry points / actions / tooling reference
10. Tests
11. Critical gotchas & learnings
12. Development journey
13. Issue-tracker state
14. Open issues & recommended next steps
15. Cheat sheet
16. How to update this document (maintenance recipe)

---

## 1. Project overview
A Kodi (Python 3, `requires-python >=3.9`) add-on, **`script.oppo203.iso.external`**, that
hands off 4K/UHD disc-style playback from Kodi to an OPPO UDP-203/205 (or compatible clone)
over IP control, with a first-run setup wizard, optional TV-input switching, optional AVR
control (disabled by default), NAS playback adapter, and Wake-on-LAN/startup auto-power.

**Posture:** software-verified only. Every release states *"hardware validation is not
performed / not claimed"* unless real tester evidence is recorded. Do not describe any
hardware path as validated without it. (See `CONTRIBUTING.md`.)

## 2. Environment & setup
- Dev OS here: Windows; shell PowerShell (Bash also available). Python via a repo-local
  **`.venv`** (gitignored): `python -m venv .venv` then
  `.venv\Scripts\python.exe -m pip install -r requirements-dev.txt` (pytest, pytest-xdist,
  coverage, PyYAML, ruff, mypy, typing-extensions; `paramiko` also installed locally for the
  dev SSH restart).
- On-device testing target: a **CoreELEC** box on the LAN, reachable at SMB
  `\\COREELEC\Addons` (auth in Windows Credential Manager) and SSH (`root`, key-based).
  **No credentials are committed** — they live in Credential Manager / on the device.

### Environment readiness checklist (the `resume` preflight runs this)
Before any work, confirm each row. The **resume** flow checks these, **auto-installs** the
ones marked *auto* (idempotent), and **pauses** for the *manual* ones with the exact fix.

| # | Requirement | Needed for | Check (Windows; use `.venv/bin/python` on POSIX) | Fix if missing | Mode |
|---|---|---|---|---|---|
| 1 | Python ≥ 3.9 (3.12 here) | runtime + all tests | `python --version` | install Python 3.12, then re-create the venv | manual |
| 2 | repo-local `.venv` | isolated dev env | `.venv\Scripts\python.exe --version` | `python -m venv .venv` | auto |
| 3 | dev deps (pytest, pytest-xdist, coverage, PyYAML, ruff, mypy, typing-extensions) | tests, lint, release gates | `.venv\Scripts\python.exe -c "import pytest, xdist, coverage, yaml, ruff, mypy"` | `.venv\Scripts\python.exe -m pip install -r requirements-dev.txt` | auto |
| 4 | paramiko (local only) | `tools/dev_build.py` SSH restart | `.venv\Scripts\python.exe -c "import paramiko"` | `.venv\Scripts\python.exe -m pip install paramiko` | auto |
| 5 | git | version control / PRs | `git --version` | install Git for Windows | manual |
| 6 | gh CLI, authenticated | PRs, releases, resume reporting | `gh auth status` | `gh auth login` (interactive) | manual |
| 7 | pre-push coverage hook | blocks a push if coverage drops below 99% (catch it before CI) | `git config --get core.hooksPath` → `scripts/hooks` | `git config core.hooksPath scripts/hooks` | auto |

- **Auto rows (2–4, 7)** are safe to install unattended and are idempotent — the preflight
  runs `python -m venv .venv` (only if absent), then
  `.venv\Scripts\python.exe -m pip install -r requirements-dev.txt paramiko`, and
  `git config core.hooksPath scripts/hooks`.
- **Manual rows (1, 5, 6)** are system/auth changes — never auto-installed; the preflight
  prints the fix command and stops for the maintainer.
- **Windows test note:** pytest needs the `TEMP`/`TMP` override + `--basetemp=build\_pt`
  (see §3) — already baked into the test commands, not a separate install.
- **Optional (NOT required to start coding):** on-device testing needs the CoreELEC box
  reachable via SMB `\\COREELEC\Addons` + SSH (key-based). Only `tools/dev_build.py` uses it;
  code + the full test suite run fully offline.
- **Last assessed:** 2026-05-23 — all rows green (Python 3.12.10, `.venv` ok, pytest 8.4.2 /
  pytest-xdist 3.8 / coverage 7.14 / PyYAML 6.0.3 / ruff 0.15.14 / mypy 1.20.2 / paramiko
  5.0.0, git 2.53, gh 2.92 authed as `skull-01`).

## 3. How to run / test / validate (exact commands)
**Run the add-on on real hardware (fast dev loop):**
```
.venv\Scripts\python.exe tools\dev_build.py
```
Builds from the working tree, stamps an auto-incrementing dev version, syncs to the
CoreELEC addons dir, and restarts Kodi over SSH. Dev-only — never publish those builds.

**Full test suite (parallel, ~16s). Windows needs the temp workaround:**
```
$env:TEMP = (Resolve-Path "build\_tmp").Path; $env:TMP = $env:TEMP
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
.venv\Scripts\python.exe -m pytest -q -n auto -p xdist --dist worksteal --basetemp="build\_pt"
```
> `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` matches CI's deterministic plugin set, so xdist is **not**
> autoloaded — pass `-p xdist` to load it explicitly, otherwise `-n auto` errors with
> "unrecognized arguments: -n". `--dist worksteal` rebalances the few subprocess-spawning
> tests (the slow tail) across idle workers — a small but free win over the default `load`.

**Coverage gate (parallel via pytest-cov, ~13–25s; floor 99%, no omit):**
```
$env:TEMP = (Resolve-Path "build\_tmp").Path; $env:TMP = $env:TEMP
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
.venv\Scripts\python.exe -m pytest -q -p xdist -p pytest_cov -n auto --dist worksteal --cov=resources/lib --cov-report=term-missing --basetemp="build\_pt"
```
> `pytest-cov` measures each xdist worker correctly (whole `resources/lib`, **no** module-level
> omit) — currently 5593 stmts, ≈99.1%, floor `fail_under=99` enforced. A **pre-push hook**
> (`scripts/hooks/pre-push`, enabled with `git config core.hooksPath scripts/hooks`) runs this
> same gate automatically and blocks a push if coverage drops — bypass with `git push
> --no-verify`. Do **NOT** use plain `coverage run -m pytest -n auto`: that leaves xdist workers
> unmeasured (reads ~0%). CI keeps the serial `coverage run` form (2-core runners; pinned by
> `test_github_readiness_g6_ci_hardening.py`).

**Lint/format (CI scope only):**
```
.venv\Scripts\python.exe -m ruff check resources default.py service.py
.venv\Scripts\python.exe -m ruff format --check resources default.py service.py
```

**Release gates:**
```
.venv\Scripts\python.exe tools\sync_version.py --check --expected-version <ver>
.venv\Scripts\python.exe tools\render_docs.py --check
.venv\Scripts\python.exe tools\audit_release.py --expected-version <ver>
```

## 4. Build norms
- **Releases are tag-driven:** push a `v*` tag → `.github/workflows/package.yml` builds the
  ZIP + SHA256 and creates the GitHub Release. Use the **`/release`** runbook
  (`.claude/commands/release.md`).
- **Branch + PR to `main`**, merge with a merge commit and **always delete the branch**
  (`gh pr merge --merge --delete-branch`); then prune any leftover merged local branches
  (`git branch -d <name>`, `git fetch --prune`). No direct commits to `main` for code, and
  never leave merged branches lying around.
- **Two-tier version pinning (~78 files):** "active" locations change every release;
  "frozen evidence" (`docs/release-history/`, `release-evidence/`, `docs/github-readiness/`,
  `docs/ai-handoff/`, historical `addon.xml` narrative sentences, historical test
  assertions) must NOT change. See the guide §3.2.
- **Per-release evidence:** 8 docs under `docs/release-history/` + `release-evidence/
  v<ver>-final/MANIFEST.txt`; some content checked by `tests/test_v2910_final_release.py`.
- **Commit messages:** plain; **no `Co-Authored-By` agent footer** (the harness blocks it).
- **Runtime ZIP cleanliness:** only `addon.xml`, `default.py`, `service.py`, `resources/`,
  and allowlisted assets ship; tests/tools/docs/handoff files never ship.

## 5. Documentation & workflow conventions
- Generated docs (`README.md`, `reference.md`, `web-references.md`) come from
  `docs/sources.yaml` via `tools/render_docs.py --write` — do not hand-edit the generated
  blocks.
- `addon.xml` `<description>` is a **cumulative** narrative (prepend a new sentence each
  release; keep history).
- Release notes follow a fixed shape: intro, `## Highlights`, `## Runtime behavior`,
  `## Hardware validation` ("software-verified only…not performed / not claimed").
- `CONTRIBUTING.md` is authoritative for contributor norms (conservative changes +
  regression tests; honest validation claims; AI build-notes discipline).

## 6. Architecture / module map
- `default.py` → `resources.lib.installer.main()` — first-run wizard (if not completed) +
  the action menu.
- `service.py` — Kodi service; intercepts disc playback (`[OPPO203][SERVICE]` logs).
- `resources/lib/`:
  - `wizard.py` / `first_run_wizard.py` / `wizard_polish.py` — the wizard UI flow.
  - `installer.py` — menu, file generation (playercorefactory + keymap), auto-install.
  - `external_player.py` — the external-player entry Kodi launches per playercorefactory.
  - `oppo_control.py` / `oppo_remote.py` / `oppo_tcp_client.py` — OPPO IP control (TCP 23).
  - `hardware_presets.py` (wizard dropdown + command quirks), `hardware_profiles.py`
    (canonical registry + aliases), `hardware_capabilities.py`, `settings_reader.py`
    (model normalization + compat) — **the 4 layers that must agree** (see gotchas).
  - `playercorefactory_merge.py` — safe merge into an existing playercorefactory.xml.
  - `intercept.py`, `disc_classification.py` — 4K disc-tag routing logic.
  - `tv_*`, `avr_*`, `smartthings_control.py`, `roku_ecp_control.py`, `adb_control.py` —
    TV/AVR backends. `nas_playback_adapter.py`, `path_mapper.py`, `reconnect_backoff.py`,
    `diagnostic_*`, `i18n.py`, `constants.py`, `version.py`.

## 7. Data model & config schema
- User settings: `resources/settings.xml` (Kodi schema); read via `settings_reader.py` and
  `installer.get_setting`/`bool_setting`. Key settings: `oppo_ip`, `oppo_port`,
  `oppo_hardware_model`, `playback_architecture` (`external_player`|`service_interception`),
  `python_path`, `wizard_completed`, startup-power/WoL keys, TV/AVR keys.
- OPPO command map: `resources/data/oppo_command_map.json` (76 keys; audited).
- Localization: `resources/language/resource.language.*/strings.po` (12 locales; each needs
  the gettext header — see gotchas).
- Release/doc metadata: `docs/sources.yaml`. Version source of truth:
  `resources/lib/version.py` (mirrored to `addon.xml` by `tools/sync_version.py`).

## 8. Key flows / pipelines
- **First-run wizard:** `default.py` → `installer.main()` → `wizard.run_wizard()` (mode,
  network probe, hardware model, power/wake, architecture) → optional auto-install of setup
  files into Kodi userdata.
- **external_player routing:** generated `playercorefactory.xml` routes tagged 4K/UHD
  disc-style sources (ISO/BDMV/MPLS containing `4K`/`UHD`/`2160p`) to `external_player.py`,
  which sends OPPO commands. Loose video files stay with Kodi.
- **service_interception:** `service.py` watches `Player.OnPlay` and redirects disc playback.
- **Chinoppo clones:** eject-to-wake quirk (`#EJT` to power on, `#EJT`+`#PLA` to play).
- **Release pipeline:** version bump → evidence → PR → merge → tag → `package.yml` builds +
  publishes. **Dev pipeline:** `tools/dev_build.py` (build → sync → restart Kodi).

## 9. Entry points / actions / tooling reference
- **Kodi entry points:** `default.py` (script), `service.py` (service) — declared in
  `addon.xml`. The script menu (in `installer.main()`) offers: generate playercorefactory,
  generate keymap, open settings, preview files, architecture dialog, OPPO discovery, TCL
  presets, file-list diagnostic, run/reset wizard, AutoScript, export readiness/AVR reports.
- **Dev/release CLI (`tools/`):** `dev_build.py`, `sync_version.py`, `render_docs.py`,
  `audit_release.py`, `package_installable_zip.py`, `i18n_extract.py`, `make_pot.py`,
  `test_layout.py`, `type_check.py`. **Scripts:** `scripts/package_release.sh`,
  `scripts/verify.sh`.
- **Slash commands (`.claude/commands/`):** `/release`, `/resume`, `/done-for-the-day`.

## 10. Tests
- Runner: `pytest` (parallel via `pytest-xdist`). Pure-Python; Kodi APIs faked via
  `tests/_stubs`. No `conftest.py`; each test sets up `sys.path`.
- CI (`.github/workflows/ci.yml`): Release gate (full suite + coverage + audit),
  Lint/format, Compatibility smoke (3.9/3.10/3.12). `package.yml` builds the ZIP.
- Coverage floor **99%** across all of `resources/lib` (no module-level omit; UI/glue
  modules are back in measurement). Actual ≈99.2%; a few on-device package-import shims are
  `# pragma: no cover`. See `docs/testing-strategy.md`.
- **`claude-review` CI check is broken** (bot/secret) and always fails — not a blocker.

## 11. Critical gotchas & learnings
- **Bare-import trap:** on-device, modules load as `resources.lib.*`; bare
  `from wizard import …` fails (`No module named 'wizard'`). `installer.py` adds its dir to
  `sys.path`; new sibling imports must use that or try-relative/except-bare. (Fixed on
  `wip/wizard-ux`.)
- **Locale `.po` header:** every `strings.po` needs the gettext header or Kodi logs
  `POParser: unable to read PO file header` and loads no translations. (Fixed on
  `wip/wizard-ux`; the audit's locale check was relaxed to allow the one header entry.)
- **Hardware models live in 4 layers** (`hardware_presets`, `hardware_profiles`,
  `hardware_capabilities`, `settings_reader`) — keep them in sync; the wizard dropdown
  (`hardware_presets`) is the one that tends to lag.
- **Windows pytest** needs `TEMP`/`TMP` override + `--basetemp=build\_pt` (`WinError 5`).
- **Coverage + xdist:** never run the coverage gate with `-n auto` (workers unmeasured).
- **Version bump:** never edit frozen evidence; one historical `fail_under=98` in
  `test_all.py` reads a frozen doc — do not change it.

## 12. Development journey (commit → what/why)
- `d6e3470` Merge #14 — session-continuity system: root `AI_RESUME_HANDOFF.md`,
  `AGENTS.md`/`CLAUDE.md` triggers, `/resume` + `/done-for-the-day` commands.
- `0f56f17` Merge #13 — AI handoff guide on `main`; `/resume`; `/release` refreshes guide.
- `a31e62b`/`dddb3d7` Add then relocate the AI resume guide (canonical on `main`).
- `8f594e1` Add missing player presets (M9205 V1, M9200, CineUltra, IPUK, GIEC) — wizard
  dropdown lagged the registry.
- `bed4f92` Wizard installs setup files directly into Kodi (merge + backup).
- `867206a` Wizard shows generated setup-file locations.
- `dbae4d7` Fix missing PO header in all 12 locales (Kodi POParser error).
- `0d64322` Fix first-run wizard `No module named 'wizard'` (installer sys.path).
- `9213a15`/`e754b89`/`d371da7` `tools/dev_build.py` — fast Kodi iteration (build→sync→restart).
- `2abe409`/`84688dd` Release **v2.9.13** (testing-strategy + tooling; no runtime change).
- `144438f`/`dce3112` `/release` runbook.
- `851bb34`/`99f26f5` Parallel tests (pytest-xdist) + audit no longer recompiles `.venv`
  (229s→16s).
- `bd11744`/`aa684e0` Testing strategy: coverage 98→50, omit UI/glue, Black→ruff format.
- `6c15b01`/`965ad25` Release **v2.9.12** (ready-to-transfer files + add-on icon).
- (Full detail + rationale: `docs/ai-handoff/AI_RESUME_GUIDE.md` §8.)

## 13. Issue-tracker state
No GitHub **Issues** are used; work is tracked as **Pull Requests**. As of last sync the 5
most recent PRs (#9–#13) are all **merged** (see journey). Latest release: **v2.9.13**.
Refresh with `gh pr list --state all --limit 10` and `gh release list --limit 3`.

## 14. Open issues & recommended next steps
1. **Ship v2.9.14** — `wip/wizard-ux` is staged, green, and pushed. Confirm on-device UX,
   then run `/release` (it changes runtime behavior; note that in the release notes).
2. **Fix the broken `claude-review` CI workflow** (bot/secret) so automated review returns.
3. ~~Restore 99% coverage~~ — **done**: floor restored to 99% with UI modules re-measured
   (no omit); see `docs/testing-strategy.md`.

## 15. Cheat sheet
| Action | Command |
|---|---|
| Resume context | type `resume` (or `/resume`) |
| Stop cleanly | type `done for the day` (or `/done-for-the-day`) |
| Fast on-device build | `.venv\Scripts\python.exe tools\dev_build.py` |
| Test (parallel) | `pytest -n auto` (+ Windows temp workaround) |
| Coverage gate | `pytest -p xdist -p pytest_cov -n auto --dist worksteal --cov=resources/lib` (~25s) |
| Lint/format | `ruff check`/`ruff format --check` on `resources default.py service.py` |
| Cut a release | `/release` (or `/release <ver>`) |
| Update this doc | `update AI_RESUME_HANDOFF.md` (recipe below) |

## 16. How to update this document (maintenance recipe)
Run these and write each result into the matching section — deterministic, not by judgment:

1. **Header "last sync ≈ commit":** `git fetch origin -q && git rev-parse --short origin/main`
   → update the header SHA.
2. **Header "Tests on `main`":** check out / be on the target branch, run the parallel test
   command (§3), and record the `N passed, M skipped` line.
3. **§12 Development journey:** `git log --oneline -15` → prepend new commits (SHA → what/why).
4. **§13 Issue-tracker state + §1 "Latest release":** `gh pr list --state all --limit 10`,
   `gh release list --limit 3` → update.
5. **§14 Open issues & next steps:** `gh pr list --state open` and
   `git branch -r --no-merged origin/main` → update the backlog/branches.
6. **Work in progress:** set manually during `done for the day` (date, commit, task, done,
   left, key files, related PR/branch, tests pass?).
7. **§10 Tests / §4 norms:** only when CI, the coverage gate, or release norms change.

After editing, commit & push the doc (on `main`; see the `done for the day` recipe).
