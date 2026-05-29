# Manual Verification Checklist

**Purpose:** the operator's queue of "agent claimed done; operator must verify before
closing the issue." Per the **only-operator-closes-issues** norm, agents never call
`gh issue close` and never write `Closes/Fixes/Resolves #N` — instead they comment the
implementing SHA(s) on the issue and append a row here.

## How to use

- **Agents:** when work seems done, append an entry under the right phase. Include the
  issue number, the implementing SHA(s), and the exact steps the operator should run to
  confirm.
- **Operator:** work the list top-down. When a row passes Phase C, close the GitHub
  issue and check the row off (or strike it out and move to a "Verified" archive section
  at the bottom).

## Phase definitions

- **Phase A — pre-merge.** PR is open. Operator verifies the diff makes sense, CI is
  green, and the change does what the issue says. Block: anything that should be fixed in
  the PR before merge.
- **Phase B — post-merge sanity.** PR is merged to `main`. Operator confirms `main` still
  builds + tests, nothing visible is broken. Block: a regression caught here typically
  means a hotfix or revert, not a slow re-verification cycle.
- **Phase C — operator end-to-end verify.** Operator runs the change in the real
  environment (Kodi on the actual box, the configurator on the actual Windows host,
  against the actual hardware chain). This is the **only** step that authorizes closing
  the issue.

---

## Phase A — pre-merge

### ENH-#43 — Split `resources/lib` into tv / oppo / avr / kodi sub-packages

- **Implementing SHA:** head of `claude/enh43-lib-subpackages-r9k2m4x7` (commented on issue #43).
- **Diff size:** 46 modules moved into `resources/lib/{tv,oppo,avr,kodi}/`; file moves only — no function/API renames.
- **What changed:**
  - A lazy `sys.meta_path` alias finder in [`resources/lib/__init__.py`](../resources/lib/__init__.py)
    keeps legacy flat names (`resources.lib.oppo_control`, bare `oppo_control`) resolving to the
    **same** canonical `resources.lib.<bucket>.<module>` objects. Imports nothing eagerly
    (installer's `xbmcaddon.Addon()` stays lazy).
  - `version.py` moved to `kodi/`; `sync_version.py` sentinel + CI `package.yml`,
    `scripts/package_release.sh`, `scripts/verify.sh`, `tools/audit_release.py` updated to the
    canonical path.
  - Module-top cross-family imports made explicit (`from ..oppo.oppo_control import …`); lazy
    in-function imports kept bare (finder-resolved, so existing test mocking by bare name keeps
    working). `command_map.py` data path bumped `parents[1]` → `parents[2]` (module is one level
    deeper) to keep resolving `resources/data/oppo_command_map.json`.
  - Test stub-context managers (`kodi_stubs` / `kodi_stub_context`) now purge BOTH the legacy
    alias and the canonical bucket module (via `tests/_support/lib_buckets.py`) so the finder
    doesn't leave a stale stub-bound module across tests. New `tests/__init__.py` installs the
    finder for the `unittest discover` path (which doesn't load `conftest.py`).
- **CI / gates (all green this session):** `pytest -n auto` **865 passed, 3 skipped**; serial
  coverage **99.04%** (≥ 99% gate); `ruff check` + `ruff format --check` clean; `python -m
  unittest discover -s tests` **484 OK**; `sync_version` / `test_layout` / `i18n_extract` /
  `render_docs` --check all OK; `audit_release` **580/580 PASS**; runtime ZIP = 70 files (50
  under buckets, `version.py` in `kodi/`, no dev dirs leaked).
- **Phase A review focus:**
  - The finder is the one piece of "clever" code — confirm single-identity aliasing and lazy install.
  - Spot-check a cross-bucket import (`external_player` → `..oppo` / `..tv` / `..avr`) and that
    `default.py` / `service.py` still import their entry points.
  - The 12 `# pragma: no cover` additions are all on now-dead bare-name `except ImportError:`
    fallback branches (the finder supersedes them); confirm none masks real logic.
- **Phase C — on-device smoke (when hardware is to hand):**
  1. Install the runtime ZIP in Kodi; confirm the add-on opens with no import error.
  2. Play a tagged 4K ISO; confirm handoff to the OPPO (interception + external-player path).
  3. Confirm TV input switch + AVR sequencing still fire (if enabled).
  4. Open the installer/diagnostics menu entries; confirm no import errors.
  - **Software-verified only; hardware validation not claimed.**

### PR #40 — Strip the in-Kodi setup wizard from the addon

- **Implementing SHA:** `3abf486` on `claude/strip-wizard-g4feovqi`.
- **Diff size:** 44 files; +313 / −5814 (mostly deletes).
- **Review focus:**
  - `service.py` `Monitor` is now a no-op shell (lifecycle only). Confirm
    `_service_main()` still works (it uses `Monitor()` for
    `abortRequested`/`waitForAbort`, both inherited from `xbmc.Monitor`).
  - `resources/lib/installer.py` `main()` lost the wizard auto-launch and
    menu items 9 (Run wizard), 10 (Reset wizard), 11 (AutoScript). The
    architecture-choice first-run dialog still fires when
    `architecture_choice_made` is unset.
  - `resources/settings.xml`: `<category id="wizard">` was renamed to
    `<category id="playback">` — verify no other code reads the old id.
  - `resources/lib/i18n.py` `_EN` fallback table is now empty; `L()` still
    resolves through `xbmcaddon` when Kodi is running.
  - 12 PO files: `#30910/#30920/#30930/#30940/#30950` and `#31000-#31061`
    deleted; `#32103` retitled to "Playback", `#32113` to
    "Playback-architecture knobs."
- **CI / gates:** `pytest -n auto` 865 passed, 3 skipped; coverage 99.05%
  (>= 99% gate); ruff + py_compile + tools/*.py --check all green.
- **Decision required from operator before merge:** is the behavioural change
  in `Monitor.onSettingsChanged` (no longer auto-applies compatibility
  presets when the user changes hardware model in Kodi settings) acceptable?
  The operator picked "Total strip" during the resume, so this is the agreed
  scope, but it is the headline behavioural change and worth a second look.

- **[#41](https://github.com/skull-01/script.oppo203.iso.external/issues/41)
  (ENH-: configurator owns add-on configuration — policy doc, part A)** —
  branch `claude/config-owner-policy-a3k7m2nq`. Docs-only PR adding a
  `## Configuration is owned by the configurator` section to
  [`AGENTS.md`](../AGENTS.md) and a `## Configuration ownership` section to
  [`CONTRIBUTING.md`](../CONTRIBUTING.md). Read both new sections and confirm:
  (1) the policy statement matches your intent ("configurator owns persistent
  config; add-on read-mostly"); (2) the three allowed exceptions are correct
  (per-session toggles, the #42 settings menu carve-out, diagnostic exports);
  (3) the "not allowed" list is correct (new persistent-setting categories,
  new first-run dialogs, add-on side writers for `playercorefactory.xml` /
  keymap / NAS creds). Parts B (in-add-on guidance hint) and C
  (settings-file ownership marker) are out of scope for this PR and wait
  until [#40](https://github.com/skull-01/script.oppo203.iso.external/pull/40)
  merges. No code paths exercised — docs-only.

## Phase B — post-merge sanity

_(none queued)_

## Phase C — operator end-to-end verify

_(none queued)_

---

## Verified (archive)

_Move rows here after Phase C passes and the issue is closed. Newest at the top._

_(empty)_
