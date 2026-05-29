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

## Phase B — post-merge sanity

_(none queued)_

## Phase C — operator end-to-end verify

_(none queued)_

---

## Verified (archive)

_Move rows here after Phase C passes and the issue is closed. Newest at the top._

_(empty)_
