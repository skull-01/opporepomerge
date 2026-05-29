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

- **[#41](https://github.com/skull-01/script.oppo203.iso.external/issues/41)
  Parts B + C — addon-side guidance hint + overwrite warning** — branch
  `claude/enh41-bc-config-hint-a4n9k2m`. Diff: 14 files (`service.py`,
  `resources/settings.xml`, 12 PO files, `tests/test_v2914_build1_config_owner_hint.py`,
  `tests/test_all.py` settings-count assertion 97→98).
  - **Review focus:**
    - `resources/settings.xml`: new `<setting id="config_owner_hint" label="30290"
      type="lsep"/>` at the top of `<category id="connection">` (Connection is
      the default landing page; users see the banner immediately). The lsep
      `id` is unusual but kept so the existing `test_every_setting_has_id`
      invariant holds; Kodi accepts it.
    - `service.py`:
      - New constant `CONFIGURATOR_MANAGED_KEYS` (42 keys) covering IPs,
        ports, hardware-model selectors, TV/AVR command strings, SmartThings
        and Sony tokens, and OPPO command sequences. Operator-tunable knobs
        (timeouts, retries, bools, playback timings, broadcast addresses,
        mode enums) are intentionally excluded — confirm the set matches the
        ENH-#41 policy intent.
      - New `_snapshot_managed_settings()` / `_changed_managed_keys()` /
        `_resolve_localized()` / `_notify_config_hint_once_per_session()` /
        `_warn_overwritten_managed_keys()` helpers — logging/notification
        only, no state mutation.
      - `Monitor` now overrides `__init__` (captures baseline snapshot) and
        `onSettingsChanged` (fires Part B hint once per session, then per-key
        Part C warnings for any `CONFIGURATOR_MANAGED_KEYS` entry that
        changed; baseline refreshes after each fire). PR #40's no-mutation
        invariant is preserved — the new hook only reads settings and shows
        notifications/logs.
    - 12 PO files: 4 new strings (#30290 lsep banner, #30291 short hint body,
      #30292 per-key warning template with `{key}` token, #30293 notification
      title). Non-en_gb PO files use msgid=msgstr fallback per project
      convention.
    - `tests/test_v2914_build1_config_owner_hint.py`: 21 new tests across 5
      classes covering managed-key membership invariants, snapshot/diff,
      notification once-per-session gating, per-key warning, Monitor lifecycle,
      and settings.xml/PO presence assertions.
    - `tests/test_all.py` line 897: settings count bumped 97→98 (the new
      lsep adds a passive label row); test comment updated.
  - **Kodi-API caveat:** Kodi has no "settings dialog opened" event. The only
    `xbmc.Monitor` hook for settings is `onSettingsChanged`, which fires
    after a user saves a change. So Part B's "first-open-per-session"
    notification is implemented as "first **change** per session" — the
    always-visible `lsep` banner is the on-open counterpart.
  - **CI / gates:** `pytest -n auto --basetemp=build\_pt` 886 passed, 3
    skipped in ~9.5s; `ruff check service.py
    tests/test_v2914_build1_config_owner_hint.py` clean. Repo-wide ruff still
    shows 257 pre-existing errors (covered by
    [ENH-#38](https://github.com/skull-01/script.oppo203.iso.external/issues/38),
    out of scope here).
  - **Operator end-to-end (Phase C) when run on hardware:**
    1. Open Kodi → Add-ons → OPPO 203 ISO External → Settings.
    2. Confirm the Connection tab shows the lsep banner text at the top
       before "Oppo IP address".
    3. Change a non-managed setting (e.g. `Reconnect retry max`) and click OK
       → expect the once-per-session notification "Most settings are managed
       by the configurator. Changes here may be overwritten." No per-key
       warning.
    4. Re-open settings, change another non-managed setting, click OK →
       expect NO notification (suppressed for the session).
    5. Re-open settings, change `Oppo IP address` to a new value, click OK →
       expect the per-key warning notification "Setting 'oppo_ip' is managed
       by the configurator. Re-run the configurator to make this change
       permanent." Kodi log shows
       `[OPPO203][SERVICE] Configurator-managed key 'oppo_ip' was overwritten
       via Kodi UI.` at WARNING level.
    6. Restart Kodi → repeat step 3 → the once-per-session notification fires
       again (Window(10000) property cleared on restart).

### ENH-#42 — Minimal in-add-on network settings menu (IP editor; PR 1 of 2)

- **Implementing SHA:** head of `claude/enh42-network-editor-k4n9x2p7` (commented on issue #42).
- **Scope:** PR 1 of 2 for ENH-#42 — the network/IP viewer-editor only. The
  language switcher ships as PR 2.
- **What changed:**
  - [`resources/lib/kodi/installer.py`](../resources/lib/kodi/installer.py): new
    menu entry "Network settings (TV / OPPO / AVR / Kodi)" in `main()` (choice
    11, before Cancel), plus `network_settings_menu()`, `_network_fields()`, and
    `_resolve_enum()`. The editor surfaces the configurator-managed connection
    fields and lets the user override one in place.
  - Fields are **backend-aware**: always OPPO IP/port + TV IP; then the active
    `tv_backend`'s host fields (ADB port + path / Sony PSK / Roku ECP port /
    SmartThings token + device id); AVR host/port when AVR is enabled or a
    backend is selected (+ Sony AVR PSK for `sony_audio_api`). The Kodi box
    address is shown **read-only** — there is no in-add-on setting for it
    (configurator-owned).
  - Every editable key is in `service.CONFIGURATOR_MANAGED_KEYS`, so a top
    "[Managed by the configurator]" row explains overrides may be overwritten,
    and each successful edit repeats that note. Empty/unchanged input is a no-op
    (won't clear a value); non-numeric port input is rejected.
  - `tests/test_v2914_build2_network_settings_menu.py`: 21 new tests (menu entry
    + dispatch, backend-aware field list incl. enum-index normalization,
    edit/write-back, invalid-port reject, no-op, read-only Kodi row, managed
    marker).
  - `tests/test_coverage_hardening.py`: menu-shape test updated 11→12 choices.
- **CI / gates (software-verified only; hardware validation not claimed):**
  `pytest -n auto` 907 passed / 3 skipped; serial coverage 99%
  (`installer.py` 99%, new code fully covered); `ruff check` +
  `ruff format --check resources default.py service.py` clean; `unittest
  discover` 526 OK; `audit_release` 578/578; py_compile +
  render_docs/sync_version/test_layout/i18n `--check` all green.
- **Operator end-to-end (Phase C) when run on hardware:**
  1. Open Kodi → Add-ons → OPPO 203 ISO External → run the add-on (its own
     menu, not Kodi's generic Settings panel).
  2. Select "Network settings (TV / OPPO / AVR / Kodi)".
  3. Confirm the first row reads "[Managed by the configurator] - select for
     details"; selecting it shows the managed-by-configurator explanation.
  4. Confirm OPPO IP / OPPO port / TV IP rows show current values, and the
     TV/AVR rows match the configured backend (e.g. ADB → TV ADB port + ADB
     binary path).
  5. Select "OPPO IP", enter a new value → expect "Setting updated" with the
     managed-override note; re-open and confirm `oppo_ip` persisted.
  6. Select "OPPO port", enter letters → expect "Invalid port" and no change.
  7. Select "Kodi box address" → expect the read-only explanation (no input
     prompt).
  8. Select "Back" → returns to the main add-on menu.

### ENH-#42 — In-add-on add-on-language switcher (PR 2 of 2)

- **Implementing SHA:** head of `claude/enh42-language-switcher-q8m3v7k2` (commented on issue #42).
- **Stacked on** the PR 1 network-editor branch (both touch `installer.main()` + the menu-shape test); **merge PR 1 first**.
- **Scope:** the language half of ENH-#42. Open question #1 ("follow Kodi system language") is included per the issue's acceptance criteria.
- **What changed:**
  - [`resources/lib/kodi/i18n.py`](../resources/lib/kodi/i18n.py): `supported_languages()` fixed 7 → 12 (it was stale, omitting ja/ko/pl/pt/ru); new `language_options()`, `effective_language()` (resolves the `addon_language` setting — follow-Kodi maps `xbmc.getLanguage()` → bundled locale, en_gb fallback), and a small per-locale `strings.po` reader so `L()` consults a pinned locale first. The default follow-Kodi path is unchanged.
  - [`resources/settings.xml`](../resources/settings.xml): hidden `addon_language` setting (`visible="false"`, default `follow_kodi`), driven from the add-on menu rather than Kodi's settings panel (settings count 98 → 99; label reuses an existing string id since it is never displayed).
  - [`resources/lib/kodi/installer.py`](../resources/lib/kodi/installer.py): new "Add-on language" menu entry (choice 12) + `language_menu()`.
  - Tests: `tests/test_v2914_build3_language_switcher.py` (25 tests incl. the follow-Kodi stub path); `tests/test_all.py` supported-languages 7→12 + settings count 98→99; `tests/test_coverage_hardening.py` menu-shape 12→13.
  - **Honest caveat:** the 12 bundled non-en_gb `strings.po` files are currently English placeholders (msgstr == msgid), and Kodi renders `settings.xml` labels in its own GUI language. So pinning a locale changes the source file `L()` consults but does **not** yet change visible text — the mechanism is in place for when translations are populated. Today only the configurator-owner notifications (ids 30290–30293) route through `L()`.
- **CI / gates (software-verified only; hardware validation not claimed):** `pytest -n auto` 932 passed / 3 skipped; serial coverage 99% (`i18n.py` 100%); `ruff check` + `ruff format --check resources default.py service.py` clean; `unittest discover` 551 OK; `audit_release` 578/578; doc/version/layout/i18n `--check` green.
- **Operator end-to-end (Phase C) when run on hardware:**
  1. Open Kodi → Add-ons → OPPO 203 ISO External → run the add-on.
  2. Select "Add-on language".
  3. Confirm the list shows "Follow Kodi system language" first (marked "(current)" by default) then the 12 locales.
  4. Pick a locale → expect "Add-on language preference saved: …"; re-open and confirm it is now marked "(current)".
  5. Pick "Follow Kodi system language" → expect the confirmation naming the resolved locale (matches Kodi's UI language).
  6. Translation note: menu and settings labels remain English — see the placeholder caveat above.

### ENH-#51 — Incremental mypy --strict gate (PR 1 of N)

- **Implementing SHA:** merged to `main` at `aa0cf68` (implementation commit `62d811f`; commented on issue #51).
- **Scope:** PR 1 of the source-only `mypy --strict` rollout. Stands up the gate
  + tooling and annotates the first leaf-module batch; the remaining ~28 modules
  follow in later PRs. Source baseline measured this session: **788 strict
  errors / 35 modules** at `--python-version 3.9`.
- **What changed:**
  - [`mypy.ini`](../mypy.ini) (authoritative) + [`pyproject.toml`](../pyproject.toml)
    `[tool.mypy]` mirror: `python_version` 3.10 → 3.9 (matches `ruff py39` /
    `requires-python >=3.9`), `strict = True`, `follow_imports = silent`, and a
    curated `files` allowlist (7 modules). The now-unused `[mypy-tests.*]` /
    `tests.*` override was dropped (no invocation type-checks tests;
    `warn_unused_configs` flagged it).
  - [`tools/type_check.py`](../tools/type_check.py): new blocking `--gate` mode
    that runs mypy over the `files` allowlist (no explicit targets, so the config
    `files` apply) and returns mypy's exit code. The default invocation stays
    non-blocking for release safety; `build_mypy_command` still targets
    `resources/lib`.
  - [`.github/workflows/ci.yml`](../.github/workflows/ci.yml): new `types` job
    runs `python tools/type_check.py --gate` (Python 3.11 runner; mypy targets 3.9).
  - 7 leaf modules annotated to zero strict errors across all four buckets:
    `avr/avr_sequence`, `kodi/keymap_skin`, `tv/smartthings_control`,
    `tv/roku_ecp_control`, `oppo/reconnect_backoff`, `oppo/autoscript_helper`,
    `tv/adb_control`. Changes are signatures + removing stale `# type: ignore`
    comments + two locals pinned (`raw: float`, `body: str`) — **no logic changes.**
    `nas_playback_adapter` was deliberately deferred (it cascades into
    `settings_reader` / `oppo_control`).
  - Guard tests updated in lockstep: `test_v291_build13_type_hint_baseline.py`
    (asserts `python_version 3.9` + strict/follow_imports/files + the gate command
    shape) and `test_github_readiness_g6_ci_hardening.py` (expects the `types` job
    and the gate command in CI).
- **CI / gates (software-verified only; hardware validation not claimed):**
  `pytest -n auto` **933 passed / 3 skipped**; serial coverage **99%**; `ruff
  check .` + `ruff format --check .` clean; `mypy --gate` clean (7 modules, 0
  errors); `unittest discover` **551 OK**; `audit_release` **580/580**;
  py_compile + render_docs/sync_version/test_layout/i18n `--check` all green.
- **Phase A review focus:**
  - The `files` allowlist + `follow_imports = silent` is the mechanism — confirm
    only listed modules are gate-enforced and the rest are silently followed (so
    the ~760 remaining strict findings do not block).
  - Confirm the gate is wired so it can be a required check (the `types` CI job)
    and that the default `type_check.py` stays non-blocking for releases.
  - Spot-check a couple of annotations (e.g. `reconnect_backoff.compute_delay`'s
    `rng: Callable[[], float] | None`) for correctness.
- **No Phase C / on-device step:** this PR changes typing config, dev tooling,
  and CI only — no runtime code paths, settings, or hardware behavior change.

### ENH-#51 — mypy --strict allowlist expansion (PR 2 of N)

- **Implementing SHA:** head of `claude/enh51-mypy-pr2-k3n8m2q6` on draft PR #54
  (commented on issue #51).
- **Scope:** PR 2 of the source-only rollout. Expands the gate `files=` allowlist
  7 → 23 modules. No gate/tooling/CI changes — those landed in PR 1 (#53).
- **What changed:**
  - [`mypy.ini`](../mypy.ini) (authoritative) + [`pyproject.toml`](../pyproject.toml)
    `[tool.mypy]` mirror: 16 modules added to `files=` (kept sorted by path).
  - 12 already strict-clean modules locked in with **no code change**:
    `avr_presets`, `avr_types`, `disc_classification`, `settings_schema`,
    `version`, `command_map`, `constants`, `hardware_capabilities`,
    `hardware_profiles`, `path_mapper`, `tv_backends`, `tv_presets`.
  - 4 leaf modules annotated to zero strict errors — signatures + pinned locals,
    **no logic changes**: `kodi/arch_benchmark.py`, `kodi/diagnostic_logging.py`,
    `kodi/i18n.py`, `tv/tv_control.py`. `tv_control` hoists an identical
    smartthings call above a no-op `acknowledged` branch to pin its
    `dict[str, object]` return type (behaviour-preserving).
- **CI / gates (software-verified only; hardware validation not claimed):**
  `tools/type_check.py --gate` **23 files, 0 errors**; `pytest -n auto`
  **933 passed / 3 skipped**; `ruff check .` + `ruff format --check .` clean;
  `unittest discover` **551 OK**; py_compile + render_docs / sync_version /
  test_layout / i18n_extract `--check` all green.
- **Phase A review focus:**
  - Confirm the 4 annotated modules are signature/typing-only (no behaviour
    change) — especially `tv_control`'s smartthings hoist and the pinned locals
    in `i18n.L` / `arch_benchmark.benchmark`.
  - Confirm the 12 zero-change modules belong in the allowlist (already
    strict-clean; the gate now prevents regressions).
- **No Phase C / on-device step:** typing/allowlist only — no runtime code paths,
  settings, or hardware behavior change.

### ENH-#51 — mypy --strict allowlist expansion (PR 3 of N: the avr_* backends)

- **Implementing SHA:** `d36e76f` on `claude/enh51-mypy-pr3-avr-x7m2k9q4` (draft PR #55;
  commented on issue #51).
- **Scope:** PR 3 of the source-only rollout. **Stacked on PR #54** (base = the PR 2
  branch); **merge #54 first.** Expands the gate `files=` allowlist 23 → 28 modules by
  annotating the five remaining AVR backends. No gate/tooling/CI changes (PR 1).
- **What changed (type-only, behaviour-preserving):**
  - [`mypy.ini`](../mypy.ini) (authoritative) + [`pyproject.toml`](../pyproject.toml)
    `[tool.mypy]` mirror: 5 modules added to `files=` (kept sorted by path).
  - `avr/avr_denon_marantz` + `avr/avr_onkyo_eiscp`: the per-command socket was typed
    `object`; annotated it as the module's existing `SocketLike` Protocol and `cast()` the
    socket-factory result so `sendall`/`recv` typecheck.
  - `avr/avr_yamaha` + `avr/avr_sony_audio`: pin `urlopen().read()` to `bytes`; `cast()`
    the `int()`/`list()`/`map()` inputs and the `meta.get()` warning/missing tuples that
    type as `object`.
  - `avr/avr_diagnostics`: a `dict -> dict` `@overload` on `sanitize_payload` so the
    dict-returning helpers stop leaking `Any`; one local pinned; 2 stale `# type: ignore`
    removed.
  - **Latent Python 3.9 import bug fixed:** the `HttpGet`/`SonyPost` aliases used PEP 604
    `bytes | str`. These are module-level assignments (eagerly evaluated, not lazied by
    `from __future__ import annotations`), so on the project's 3.9 floor they raise
    `TypeError` at import. The full suite runs on 3.11 and the 3.9 compat-smoke job does
    not import these modules, so it was never hit. Switched to `typing.Union`.
- **CI / gates (software-verified only; hardware validation not claimed):**
  `tools/type_check.py --gate` **28 files, 0 errors**; `pytest -n auto` **933 passed /
  3 skipped**; serial coverage **99%** (`avr_diagnostics` 0 missed — overloads cost
  nothing); `ruff check .` + `ruff format --check .` clean; `unittest discover` **551 OK**;
  py_compile + render_docs / sync_version / test_layout / i18n_extract `--check` all green.
- **Phase A review focus:**
  - Confirm the 5 modules are signature/typing-only — especially the socket-factory
    `cast()` and the `sanitize_payload` `@overload`.
  - Confirm the `bytes | str` → `Union` change is the intended 3.9 fix.
- **Phase A — Python 3.9 import smoke (recommended).** On a 3.9 interpreter, confirm
  `import resources.lib.avr.avr_yamaha` and `import resources.lib.avr.avr_sony_audio` no
  longer raise `TypeError`. The hosted CI 3.9 job does not import these modules, so this is
  the only place that exercises the fix on 3.9.
- **No Phase C / on-device step:** typing/allowlist only — no runtime code paths, settings,
  or hardware behavior change.

## Phase B — post-merge sanity

_(none queued)_

## Phase C — operator end-to-end verify

_(none queued)_

---

## Verified (archive)

_Move rows here after Phase C passes and the issue is closed. Newest at the top._

_(empty)_
