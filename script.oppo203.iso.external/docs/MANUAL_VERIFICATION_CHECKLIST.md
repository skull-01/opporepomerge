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

### Configurator — dedicated Step-5 receiver restore-input field (AVR-chain restore, #138 follow-up)

- **Branch:** `claude/avr-receiver-restore-input-a7f2c419`. PR-only theme (no tracked issue); follow-up to PR #138.
- **What changed (software-verified only):** Step 5 now captures a dedicated **"Kodi input on the receiver"** field (`state.avrKodiInput`), shown only in the AVR chain for native (non-Sony) backends. `mapping.ts` sources `avr_restore_input` from it instead of reusing the TV's `kodiInput` (the Step-4 TV HDMI port). A blank value writes no restore input — the add-on treats that as a non-fatal skip (`resources/lib/avr/avr_sequence.py`). `avr_restore_input` is `type="string"` read as a free-text receiver input, so there is **no add-on change**. The end-of-wizard test summary now shows receiver inputs (not "HDMI N") in the AVR chain. TV chain unchanged (regression-pinned). `tsc --noEmit` + `tsc -b` + `vite build` + **125 vitest** green.
- **Operator verifies (Phase A):** read the `state.ts` / `mapping.ts` / `step5.tsx` / `test.tsx` diff + the updated `mapping.test.ts` cases (restore now sourced from `avrKodiInput`; the dedicated-field pin proves it is NOT `kodiInput`; blank ⇒ power-on but no restore).
- **Operator verifies (Phase C — on hardware):** in an AVR-chain setup, enter a **distinct** receiver input for the Kodi box (e.g. `CBL/SAT`), different from the player input (e.g. `BD`); confirm that on playback exit the receiver returns to the **Kodi** input — not the player input, and not a TV HDMI number. Candidate mapping — confirm against a real receiver. **Migration note:** an existing AVR-chain config that relied on the old numeric reuse should re-open Step 5 and set this field, or restore is skipped (non-fatal).

### Configurator — AVR-chain switcher settings in mapping (topology PR 3)

- **Branch:** `claude/topology-avr-switcher-map-2c7f9b1e`. PR-only theme (no tracked issue).
- **What changed (software-verified only):** for the AVR chain `mapping.ts` now also writes `avr_power_on_enabled=true` and `avr_restore_enabled`/`avr_restore_input` (reusing the Step-4 Kodi return target as the receiver restore input), and gates `tv_switching_enabled` off (the receiver is the switcher). All settings are ones the add-on already reads (`resources/lib/avr/avr_control.py`); the TV chain is unchanged (regression-pinned). `tsc -b` + `vite build` + `vitest` green.
- **Operator verifies (Phase A):** read the `mapping.ts` diff + the new `mapping.test.ts` cases.
- **Operator verifies (Phase C - on hardware):** run an AVR-chain setup end to end; confirm the receiver powers on and selects the player input on handoff and restores the Kodi input on exit, and that the TV is NOT driven. Candidate mappings - confirm against a real receiver.

### Configurator — topology-aware flow + chain viz (topology PR 2)

- **Branch:** `claude/topology-flow-chainviz-4b1e7a3c`. PR-only theme (no tracked issue).
- **What changed (software-verified only):** the header chain shows a Receiver node for the AVR chain (ISO -> Kodi -> Receiver -> Player -> TV); Step 4 copy frames inputs as receiver inputs in the AVR chain. Pure helpers `isAvrChain` / `chainNodeIds` / `step4NextScreen` added and unit-tested. `tsc -b` + `vite build` + `vitest` green.
- **Operator verifies (Phase A):** read the diff; CI green.
- **Operator verifies (Phase C - on the built app):** pick the AVR chain at Step 0; confirm the header chain shows the Receiver node and Step 4 says "receiver input". Pick the TV chain; confirm the original 4-node chain and TV wording.

### Configurator — Step 0 playback-chain picker (PR #134-series topology, PR 1)

- **Branch:** `claude/topology-chain-picker-9f2a1c7d`. PR-only theme (no tracked issue).
- **What changed (software-verified only):** new Step 0 screen "How is your home theater wired?" sets `state.topology` (`kodi_tv_player` | `kodi_avr_tv_player`); the gate routes into it; a null/legacy value behaves as the TV chain everywhere. `tsc -b` + `vite build` + `vitest` green.
- **Operator verifies (Phase A):** read the diff; CI green.
- **Operator verifies (Phase C - on the built app):** launch the configurator; after the "I can already play ISOs" gate, confirm the chain picker appears and each tile advances to step 1 with the choice remembered.

### Add-on — default hold_mode now detects stop (tcp_qpl_poll) (#114)

- **Implementing SHA:** `5954556` on `claude/default-hold-tcp-qpl-b4d2f6a1` (draft PR — commented
  on issue #114). **Merge after the #112/#115/#116 hold-robustness PR (#129)** so the new default
  inherits the unreachable-OPPO abort.
- **Scope:** the shipped default `hold_mode` was `fixed_timeout` — a blind 180-minute sleep with no
  stop detection. Since the configurator does not write `hold_mode`, that default governed every
  unconfigured install. Changed it to `tcp_qpl_poll` (polls `#QPL`, ends on idle).
- **What changed (software-verified only):**
  - `resources/lib/kodi/settings_reader.py`: `DEFAULTS["hold_mode"]` `fixed_timeout` → `tcp_qpl_poll`.
  - `resources/settings.xml`: `hold_mode` enum `default="0"` → `default="3"` (index of `tcp_qpl_poll`).
  - `tests/test_hold_default.py` (2 tests): pins the reader default and its consistency with the
    settings.xml enum default index + `ENUM_VALUES`, so the two cannot drift.
- **CI / gates (software-verified only; hardware validation not claimed):** `pytest` **965 passed /
  3 skipped**; serial coverage **99%**; `ruff check` + `ruff format --check` clean; mypy strict gate
  **49 files, 0 errors**; `render_docs` / `test_layout` / `i18n_extract` / `sync_version` `--check`
  all OK (the settings.xml change is in sync).
- **Phase A review focus:** confirm `tcp_qpl_poll` is the right default (vs the lighter option of
  keeping `fixed_timeout` with a shorter minutes default), and that index 3 maps to `tcp_qpl_poll`.
- **Phase C — on-device:** on a fresh install (no configurator run), start a UHD-ISO handoff and
  confirm the hold polls `#QPL` and releases near actual disc-end (not a 3-hour blind hold).
  `tcp_qpl_poll` needs `oppo_ip` / `oppo_port` reachable; confirm idle detection works on the real
  OPPO.
### Add-on — diagnostics HTTP probe targets the OPPO HTTP port (#111)

- **Implementing SHA:** `bb34919` on `claude/diag-http-port-d9e1c4b2` (draft PR — commented on
  issue #111). Independent of the other robustness PRs (mergeable in any order).
- **Scope:** the diagnostics-dashboard `_http` reachability probe connected to TCP port 80, but the
  OPPO HTTP control API runs on `oppo_http_port` (default 436), so the HTTP capability line reported
  reachability against a port the device never serves. Diagnostics-only — no playback/control path.
- **What changed (software-verified only):** `default.py` `run_diagnostics_dashboard` gains an
  `http_port: int = 436` parameter; the nested `_http` probe connects to it (and reports it) instead
  of the hardcoded 80.
  - `tests/test_diag_probe_port.py` (2): the probe targets 436 by default and an explicit override,
    never 80 (socket faked, no real network call).
- **CI / gates (software-verified only; hardware validation not claimed):** `pytest` **965 passed /
  3 skipped**; serial coverage **99%**; `ruff check` + `ruff format --check` clean; mypy strict gate
  **49 files, 0 errors**.
- **Phase A review focus:** confirm 436 is the right default. `run_diagnostics_dashboard` has no
  live menu caller today (it is a tested/symbol-level entry), so the default governs; a future caller
  can thread the configured `oppo_http_port` through the new parameter.
- **Phase C — on-device:** run the diagnostics dashboard against the real OPPO and confirm the HTTP
  capability line reflects port-436 reachability (it always probed 80 before).
### Add-on — clear the ruff format CI red (#123)

- **Implementing SHA:** `6b920fd` on `claude/ruff-format-123-f1a8d3c6` (draft PR — commented on
  issue #123).
- **Scope:** the CI "Lint and format" job was red because `ruff format --check` flagged drifted test
  files (lines past 100 chars after last session's `players-models.json` rename). On current `main`
  only **two** files actually drift — `tests/test_all.py` and `tests/test_players_db_consistency.py`;
  the third the issue named (`test_v2914_build2_player_taxonomy.py`) is already formatted.
- **What changed:** `ruff format` on those two files — whitespace/layout only (a long path
  expression and a long assert message wrapped to ruff's canonical multi-line form). No test
  behavior change.
- **CI / gates (software-verified only):** `ruff format --check .` now clean (146 files); `ruff
  check` clean; `pytest` **963 passed / 3 skipped**; serial coverage **99%**; mypy strict gate
  **49 files, 0 errors**.
- **Phase A review focus:** confirm the diff is purely formatting. **No Phase C / on-device step** —
  test-file formatting only, no runtime code path.
### Configurator — AVR DB two-copy consistency guard (PR #134)

- **Branch / PR:** `claude/avr-db-consistency-a7d1f4e2` — [#134](https://github.com/skull-01/script.oppo203.iso.external/pull/134). PR-only theme (no tracked issue).
- **What changed (software-verified only):** new `configurator/src/avr_db_consistency.test.ts` pins the bundled `configurator/src/avr-db/avr-models.json` and the canonical `docs/configurator/avr-db/avr-models.json` byte-identical, plus schema invariants (schema_version 2, non-empty db_version/lineups/models, unique lineup + model ids, every model resolves to a real lineup). Test-only — no runtime/behavior change, no add-on change. `npm run build` + `vitest` (111 tests) green.
- **Operator verifies (Phase A):** read the diff; confirm the configurator CI job is green; merge when satisfied. No Phase C (test-only).

### Configurator — Step 5 receiver reachability probe (PR #135)

- **Branch / PR:** `claude/avr-step5-probe-b3c9e0d6` — [#135](https://github.com/skull-01/script.oppo203.iso.external/pull/135). PR-only theme (no tracked issue).
- **What changed (software-verified only):** Step 5's AVR control card gains a **Test reachability** button that TCP-probes the receiver's control port (Denon/Marantz 23, Yamaha 80, Onkyo/Pioneer 60128) via the existing generic `tv_port_probe` Tauri command — frontend only, no Rust change, no state-changing commands sent. Sony (authenticated HTTP/PSK API) and custom_command brands show no button. `npm run build` + `vitest` (103 tests) green; in-browser behaviour not exercised in-session.
- **Operator verifies (Phase A):** read the `step5.tsx` diff; confirm CI green.
- **Operator verifies (Phase C — on hardware):** in the built configurator, pick a real receiver, enter its IP, click **Test reachability**; confirm a reachable receiver reports the port answered and an unreachable/wrong IP reports failure cleanly (the probe sends no state-changing commands).
### Add-on — self-healing oppo203iso-active session sentinel (#117)

- **Implementing SHA:** `293015e` on `claude/sentinel-selfheal-c3e8a1b7` (draft PR — commented on
  issue #117). Independent of the other robustness PRs (mergeable in any order).
- **Scope:** a crash, power loss, or Kodi killing the external player skips the `finally` that
  removes the `oppo203iso-active` sentinel, leaving it on disk. A stale sentinel then disabled all
  service interception (`service.py`) and made the remote bridge forward keys with no active
  session (`oppo_remote.py`).
- **What changed (software-verified only):**
  - `resources/lib/kodi/settings_reader.py`: new dependency-free `session_is_active(addon_data_dir)`
    + `SESSION_MAX_AGE_SECONDS` (21600 = 6h, well beyond the longest legitimate hold). A sentinel
    whose file mtime is older than that is treated as inactive (self-healing). mtime is the
    session-start clock (the sentinel is written once), so the check is robust to unreadable
    contents.
  - `service.py` + `resources/lib/oppo/oppo_remote.py`: the two duplicated `_session_is_active`
    readers now delegate to the shared helper (resolving the duplication smell #117 noted).
  - `tests/test_session_sentinel_staleness.py` (5): missing / fresh / stale via the helper, plus
    the service and remote readers honoring staleness.
- **CI / gates (software-verified only; hardware validation not claimed):** `pytest` **970 passed /
  3 skipped**; serial coverage **99%** (`oppo_remote.py` 100%, the helper fully covered); `ruff
  check` + `ruff format --check` clean; mypy strict gate **49 files, 0 errors**.
- **Phase A review focus:** confirm 6h is a safe staleness window (longer than any real hold, short
  enough to self-heal next session); confirm using the file mtime (vs the stored timestamp) is
  acceptable as the session clock.
- **Phase C — on-device:** start a handoff, then kill Kodi mid-hold (or pull power) so the sentinel
  is left behind. Confirm: (a) on next start, a tagged 4K disc is intercepted again (not skipped);
  (b) the remote bridge does not forward keys when no session is active. A fresh sentinel (< 6h)
  must still gate correctly during a real session.

### Add-on — read-only OPPO player-status probe (documented #Q.. query battery)

- **Branch / SHA:** `claude/oppo-status-probe-8x3k9m2p` — relates to
  [#113](https://github.com/skull-01/script.oppo203.iso.external/issues/113) (verify the OPPO
  actually played the requested file). This PR delivers the **read-only diagnostic** that
  empirically confirms what the player reports; the #113 verify wiring is a follow-up built on
  its findings.
- **What changed (software-verified only):**
  - `oppo_control.py`: new `probe_player_status(settings, *, send=None, http=None)` — sends the
    documented `#Q..` query battery (`PROBE_QUERY_COMMANDS`:
    QPW/QPL/QFN/QFT/QTK/QCH/QTE/QTR/QEL/QRE/QDT/QAT/QST/QIS/QHD/QVR) over one TCP:23
    connection, classifies each reply (OK/ER/no-response, **preserving #QFN file-name case**),
    and best-effort attaches the raw HTTP `/getmovieplayinfo` payload. Plus
    `format_player_status_probe()` and a non-raising `_classify_probe_response()`. **No change
    to playback routing, OPPO payloads, or the hold modes.**
  - `installer.py`: new menu action **"Probe OPPO player status (diagnostic)"** (index 13,
    appended before Cancel so existing menu indices are unchanged) → `run_player_status_probe()`
    shows the parsed replies in a textviewer and saves a copy to
    `addon_data/oppo-status-probe.txt`.
  - Docs: `docs/OPPO_PROTOCOL_REFERENCE.md` transcribes the query/verbose tables from OPPO's
    RS-232 & IP Control Protocol (Dec 2017).
  - Tests: new `tests/test_oppo_status_probe.py` (13 tests — reply classification incl. the
    #QFN case + ER/empty/legacy/unknown forms, missing-host + unreachable handling, the HTTP
    field, a loopback `FakeOppoServer` default-send pass, the report formatter, and menu
    dispatch).
- **Software gates (this machine):** `pytest` **963 passed / 3 skipped**; coverage **99%**
  (≥99 gate, exit 0); `ruff check` + `ruff format` clean; `mypy` strict **clean** on the two
  gated files. Probe code fully covered.
- **Phase C — operator end-to-end verify (on the real Kodi box + OPPO):**
  1. Open the add-on → **"Probe OPPO player status (diagnostic)"**. With the player idle,
     confirm a report appears and `power` / `playback_status` / `firmware_version` populate.
  2. **Start a NAS-ISO handoff** (http / json_payload mode), then run the probe **during
     playback**. Record what `media_file_name` (`#QFN`) and `media_file_format` (`#QFT`)
     return — **does the ISO file name appear, or `ER INVALID`?** (This answers the open
     question for #113 exact-file verification.) Confirm `playback_status` = `PLAY` and
     `total_elapsed` advances on a second run.
  3. **Play a physical disc** (tcp_commands mode), run the probe, and record `#QDT` (disc
     type), `#QTK` / `#QCH`, and whether `#QFN` is `ER INVALID` for disc playback.
  4. Note any `#Q..` commands your firmware answers `ER` / no-response (older firmware lacks
     `#QFN`). Paste `addon_data/oppo-status-probe.txt` back so the #113 verify can use the real
     fields.

### Configurator — AVR Step 5 Sony auto-enable (PSK + acknowledgement)

- **Branch / SHA:** `claude/avr-sony-autoenable-5c9f2a3d` — **no tracked issue** (configurator
  §3b item 6 AVR follow-up; PR-only). Follows the v0.5.0 Step-5 wiring.
- **What changed (software-verified):** Step 5's Receiver-control card now captures the Sony
  Audio Control API credentials so Sony can auto-enable like the other native backends (it was
  configured-but-off before). New `WizardState` fields `avrSonyAcknowledged` / `avrSonyPsk` /
  `avrSonyPlayerInputUri`; `mapping.avrSettings()` emits `sony_avr_experimental_acknowledged` /
  `sony_avr_psk` / `sony_avr_player_input_uri` and sets `avr_control_enabled=true` for
  `sony_audio_api` **only** when acknowledgement + PSK + input URI + host + player input are all
  present — mirroring the add-on's own Sony gate (`resources/lib/avr/avr_presets.py`
  `requires_experimental_acknowledgement` + sensitive fields; `avr_control.py` Sony validation).
  PSK is a password-masked field. **No add-on change** — the `sony_avr_*` settings already exist
  in `resources/settings.xml`.
- **Software gates (this machine):** configurator `tsc -b` clean; `vitest` **103 passed**
  (mapping 24, incl. Sony enable + partial-gate cases); `npm run build` exit 0. Browser-preview:
  Step 5 → Sony → model → the URI + PSK (password) fields + acknowledgement toggle render; filling
  all of them flips the callout to "We'll enable Sony control … switch to extInput:hdmi?port=2".
- **Phase A review focus:** confirm requiring the URI-form input (in addition to the plain
  `avr_player_input`) is the right gate, and that PSK-as-secret handling reads correctly.
- **Phase C — operator end-to-end (real Sony receiver, NOT done by the agent):**
  1. Step 5 → Sony → pick a model; fill Receiver IP, player input, **Sony API input URI**
     (e.g. `extInput:hdmi?port=2`), **PSK**, and tick the experimental acknowledgement; confirm
     the green "we'll enable" callout appears (and that leaving any one blank keeps it off).
  2. Apply; confirm the deployed `settings.xml` carries `avr_backend=sony_audio_api`,
     `avr_control_enabled=true`, `sony_avr_experimental_acknowledged=true`, `sony_avr_psk`,
     `sony_avr_player_input_uri`.
  3. Trigger a UHD-ISO handoff; confirm the add-on powers on the Sony receiver and switches it to
     the configured input. **Experimental Sony driver + candidate mapping — confirm against real
     hardware.**
  - **Software-verified only; Sony Audio Control API path is experimental and not hardware-validated.**

### Configurator + add-on — Chinoppo M9205 V1 split into a distinct hardware model

- **Branch / SHA:** `claude/chinoppo-m9205-v1-split-c7m2k9p4` — **no tracked issue**
  (configurator §3b "M9205 V1 vs M9205" follow-up; PR-only). Operator confirmed on
  `resume` that M9205 V1 and the plain M9205 are **distinct devices** that share the
  M9205 eject-to-wake clone control protocol.
- **What changed (software-verified only):**
  - Add-on: new `oppo_hardware_model` enum value `chinoppo_m9205_v1`, **appended** to
    `resources/settings.xml` so existing stored enum indices are unchanged, and wired
    through `settings_reader.py` (`ENUM_VALUES`, aliases → `M9205-V1`, `HARDWARE_COMPAT`,
    `CHINOPPO_NAS_PLAYBACK_MODELS`), `hardware_profiles.py`, and
    `hardware_capabilities.py`. The new `M9205-V1` profile is an **exact mirror** of
    `M9205` (eject-to-wake `#EJT`, clone-safe, `http_api_436=False`) — no new command
    payloads. `hardware_presets.py` is unchanged (plain `M9205` has no preset entry and
    falls through to `generic_oppo_clone`; the V1 mirrors that).
  - Configurator: `players.ts` re-points the **M9205 V1** picker label to
    `chinoppo_m9205_v1` (plain **M9205** still → `chinoppo_m9205`; the "Other / clone"
    eject-to-wake default is unchanged). `CONFIGURATOR_HANDOFF.md` §4 enum order updated.
  - Tests: new `tests/test_chinoppo_m9205_v1_split.py` (5 tests, end-to-end add-on side);
    updated taxonomy-count guards (`test_all.py` 17→18, `test_v2910_build2` 17→18,
    `test_v2910_build3` set + `M9205-V1`) and configurator `players.test.ts` /
    `mapping.test.ts`.
- **Software gates (this machine):** add-on `pytest -n auto` **943 passed / 3 skipped**;
  coverage **99.06%** (≥99 gate); `ruff check` + `ruff format` clean; `mypy --gate`
  **49/0**. Configurator `tsc --noEmit` clean; `vitest` **63/63**; `npm run build` exit 0.
- **Phase A review focus:**
  - Confirm the `M9205-V1` (canonical key) / `chinoppo_m9205_v1` (enum value) naming
    reads right alongside the existing `M9205` / `M9205C` keys.
  - Confirm "mirror M9205 exactly" is the intended behavior. If the V1 actually differs
    at the protocol level, its `HARDWARE_COMPAT` / `hardware_profiles` entries need
    distinct values (this PR assumes identical control per the operator's confirmation).
- **Phase C — operator end-to-end (real hardware):**
  1. In the configurator Step 2, pick brand **Chinoppo**, model **M9205 V1**; complete
     the wizard and Apply. Confirm the deployed add-on `settings.xml` has
     `oppo_hardware_model` = `chinoppo_m9205_v1` (distinct from plain `M9205`).
  2. On the Kodi box, trigger a UHD-ISO handoff to the M9205 V1 player; confirm the
     add-on wakes it with `#EJT` (eject-to-wake), matching plain M9205 behavior.
  3. Confirm no regression for a plain **M9205** device (still `chinoppo_m9205` → `#EJT`).

### Configurator — real app icon + first MSI/NSIS bundle

- **Branch / SHA:** `claude/configurator-icon-bundle-h4n7k2p9` — icon set at
  `eb9f1cf`. **No tracked issue** (configurator polish theme; PR-only).
- **What changed (committed):**
  - Replaced the 766-byte placeholder `icon.ico` (PR #35) with a real icon set
    generated from the repo-root add-on artwork (`icon.png`, 256×256) via
    `cd configurator; npm run tauri -- icon ..\icon.png`. `tauri.conf.json`
    `bundle.icon` referenced four files (`32x32.png`, `128x128.png`,
    `icon.icns`, `icon.ico`) but only the stub `icon.ico` existed, so a release
    bundle would have failed on the three missing files.
  - Committed the standard Tauri **desktop** set only (PNG sizes + the
    `Square*Logo.png` / `StoreLogo.png` Windows-Store assets + `icon.icns`);
    the `ios/` and `android/` folders `tauri icon` also emits were pruned (this
    is a Windows desktop app). `tauri.conf.json` was **not** changed.
  - Refreshed the stale "placeholder" `src-tauri/icons/README.md`.
- **Build verification (software only):** `cd configurator; npm run tauri -- build`
  → **exit 0**, release compile ~1m13s, **2 bundles produced**:
  - MSI (WiX): `…\target\release\bundle\msi\OppoKodiAddon Configurator_0.1.0_x64_en-US.msi` (3.0 MB)
  - NSIS setup: `…\target\release\bundle\nsis\OppoKodiAddon Configurator_0.1.0_x64-setup.exe` (1.9 MB)
  - raw exe: `…\target\release\oppokodiaddon-configurator.exe` (8.4 MB)
- **Phase A review focus:**
  - Icon art is the add-on's promo image — busy/text-heavy, so the 32×32
    taskbar icon is cluttered. Operator picked this source for a first pass;
    swap in a purpose-built 1024×1024 PNG + re-run `tauri icon` to improve.
  - 256×256 source ⇒ the macOS `icon.icns` and the larger Store logos are
    upscaled; the Windows MSI/NSIS bundle only uses sizes ≤256, so its icons
    are not upscaled.
- **Phase C — operator end-to-end (on the Windows host):**
  1. Run the NSIS setup `OppoKodiAddon Configurator_0.1.0_x64-setup.exe` (or
     the MSI); confirm it installs without error.
  2. Confirm the installed app's Start-menu / desktop / taskbar icon shows the
     add-on artwork (not a generic/blank icon).
  3. Launch the app; confirm the window opens with the custom title bar and the
     configurator UI renders.
  4. Confirm the window / title-bar icon matches.
  5. Uninstall via Apps & features (or the MSI) and confirm clean removal.
  - **Software-verified only (build + bundle succeeded); installed-app
    behaviour and icon appearance not yet verified by the agent.**

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
    _(Naming note 2026-05-31: the three `tv/` backends here were later renamed
    `tv/tv_smartthings_control`, `tv/tv_roku_ecp_control`, `tv/tv_adb_control`; this entry
    records the closed PR as-shipped. See [`NAMING_CONVENTIONS.md`](NAMING_CONVENTIONS.md).)_
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

### ENH-#51 — mypy --strict allowlist expansion (PR 4 of N: import-fallback leaf modules)

- **Implementing SHA:** `7568f89` on `claude/enh51-mypy-pr4-n7k4m2qp` (draft PR #63;
  commented on issue #51).
- **Scope:** PR 4 of the source-only rollout. Branches from `main`. Expands the gate
  `files=` allowlist 28 → 33 modules by resolving the `no-redef` import-fallback idiom
  (handoff §3a) plus co-located errors in 5 leaf modules. No gate/tooling/CI changes.
- **What changed (type-only, behaviour-preserving):**
  - [`mypy.ini`](../mypy.ini) (authoritative) + [`pyproject.toml`](../pyproject.toml)
    `[tool.mypy]` mirror: 5 modules added to `files=` (kept sorted by path).
  - **Import-fallback strategy:** the ENH-#43 try (dotted) / except (bare) import fallback
    redefines names under `--strict`. The except-branch (runtime-fallback) import now
    carries a targeted `# type: ignore[no-redef]`; the canonical dotted import stays fully
    type-checked.
  - `resources/lib/__init__`: annotated the lazy alias finder/loader; `cast` the loader to
    `importlib.abc.Loader` at the `ModuleSpec` call; type-only `if TYPE_CHECKING` imports.
  - `kodi/intercept`: `_FsLike` Protocol for the duck-typed `fs` param;
    `# type: ignore[attr-defined]` on the canonical imports of constants re-exported through
    the disc_classification shared-constants hub (names exist at runtime).
  - `tv/tv_diagnostics`: `dict -> dict` `@overload` on `sanitize_payload`; `cast` the
    object-typed metadata `.get()` tuples before iterating; 4 stale `# type: ignore` removed.
  - `avr/avr_control`: `cast` object-typed `sony_meta.get()` tuples; 1 stale
    `# type: ignore` removed.
  - `oppo/oppo_tcp_client`: annotated all method signatures + instance attributes;
    `from __future__ import annotations` for the `X | None` hints.
- **CI / gates (software-verified only; hardware validation not claimed):**
  `tools/type_check.py --gate` **33 files, 0 errors**; `pytest -n auto` **938 passed /
  3 skipped**; serial coverage **99.04%**; `ruff check .` + `ruff format --check .` clean.
- **Phase A review focus:**
  - Confirm the 5 modules are signature/typing-only — especially the `_AliasLoader` `cast`,
    the `_FsLike` Protocol, and the `sanitize_payload` `@overload`.
  - Confirm the `no-redef` ignores sit only on the except-branch (bare) fallback imports.
- **No Phase C / on-device step:** typing/allowlist only — no runtime code paths, settings,
  or hardware behavior change.

### ENH-#51 — mypy --strict allowlist expansion (PR 5 of N: settings_reader + oppo_control hubs)

- **Implementing SHA:** `8b06744` on `claude/enh51-mypy-pr5-h5w8k3rq` (draft PR #64;
  commented on issue #51). **Stacked on PR #63** (base = the PR 4 branch); **merge #63 first.**
- **Scope:** PR 5 of the source-only rollout. Annotates the two heaviest un-migrated hub
  modules to zero strict errors and adds them to the gate (33 → 35): `kodi/settings_reader`
  (72 errors) and `oppo/oppo_control` (111 errors). Unblocks the cascade group (PR 6+).
- **What changed (type-only, behaviour-preserving):**
  - [`mypy.ini`](../mypy.ini) + [`pyproject.toml`](../pyproject.toml) mirror: 2 modules added.
  - `Settings.get` / `Settings.__getitem__` typed `-> Any` (the raw accessors; `get_str` /
    `get_int` / `get_bool` / `get_float` / `get_path` keep the concrete types). Avoids a
    cascade of false errors at every `settings.get(...)` call site in oppo_control.
  - oppo_control imports `Settings` under `if TYPE_CHECKING:` (annotation-only; no runtime
    import or cycle).
  - `HARDWARE_COMPAT` annotated `dict[str, dict[str, object]]`; a `dict[str, Any]` pin on the
    firmware-status result; `cast` on `urlopen().read()` and object-typed metadata tuples;
    one loop variable renamed to avoid a reuse type clash.
  - `get_lines` now coerces via `get_str` (equivalent for string settings).
- **CI / gates (software-verified only; hardware validation not claimed):**
  `tools/type_check.py --gate` **35 files, 0 errors**; `pytest -n auto` **938 passed /
  3 skipped**; serial coverage **99.04%**; `ruff check` + `ruff format --check` clean.
- **Phase A review focus:**
  - Confirm both hubs are signature/typing-only — especially the `Settings.get -> Any`
    decision and that no runtime control / HTTP / socket path changed.
  - Confirm `get_lines` via `get_str` is behaviour-preserving for string settings.
- **No Phase C / on-device step:** typing/allowlist only — no runtime code paths, settings,
  or hardware behavior change.

### ENH-#51 — mypy --strict allowlist expansion (PR 6 of N: the cascade group)

- **Implementing SHA:** `8406b43` on `claude/enh51-mypy-pr6-c8t4n2vp` (draft PR #65;
  commented on issue #51). **Stacked on PR #64** (base = the PR 5 branch); **merge
  #63 → #64 → #65 in order.**
- **Scope:** PR 6 of the source-only rollout. Annotates the seven hub-dependent "cascade"
  modules to zero strict errors and gates them (35 → 42): `oppo/discovery`,
  `oppo/hardware_presets`, `oppo/hardware_validation_readiness`, `oppo/nas_playback_adapter`,
  `kodi/diagnostics`, `kodi/diagnostic_summary`, `kodi/logging_v116`.
- **What changed (type-only, behaviour-preserving):**
  - [`mypy.ini`](../mypy.ini) + [`pyproject.toml`](../pyproject.toml) mirror: 7 modules added.
  - These were blocked on the PR 5 hubs. `nas_playback_adapter` reached zero with **no code
    change** (its errors were all calls into the now-typed hubs) — gated by config only. The
    other six got their own signature annotations.
  - Idioms: `object` for isinstance-checked/stringified params; `dict[str, object]` returns;
    `Any` for loose json/settings dicts; `cast` on object-typed `.get()` values before
    container/iteration ops; `Protocol`s for injected filesystem deps (`discovery._FS`,
    `logging_v116._FsLike`); a str/None `@overload` on `logging_v116.scrub`. All `...` stub
    bodies + `if TYPE_CHECKING:` blocks carry `# pragma: no cover`.
- **CI / gates (software-verified only; hardware validation not claimed):**
  `tools/type_check.py --gate` **42 files, 0 errors**; `pytest -n auto` **938 passed /
  3 skipped**; serial coverage **99.05%**; `ruff check` + `ruff format --check` clean.
- **Phase A review focus:**
  - Confirm all seven modules are signature/typing-only (no runtime control / IO / value
    change) — especially the injected-dependency `Protocol`s and the `scrub` `@overload`.
- **No Phase C / on-device step:** typing/allowlist only — no runtime code paths, settings,
  or hardware behavior change.

### ENH-#51 — mypy --strict allowlist expansion (PR 7 of N: hub-dependent idiom modules)

- **Implementing SHA:** `6fed436` on `claude/enh51-mypy-pr7-k2p9m4xt` (draft PR #66;
  commented on issue #51). **Stacked on PR #65** (base = the PR 6 branch); **merge
  #63 → #64 → #65 → #66 in order.**
- **Scope:** PR 7 of the source-only rollout — the final batch of the requested scope.
  Annotates the four larger no-redef import-fallback modules deferred from PR 4 to zero
  strict errors and gates them (42 → 46): `oppo/oppo_remote`, `kodi/external_player`,
  `kodi/installer`, `kodi/preset_manager`.
- **What changed (type-only, behaviour-preserving):**
  - [`mypy.ini`](../mypy.ini) + [`pyproject.toml`](../pyproject.toml) mirror: 4 modules added.
  - PR 4 no-redef strategy throughout (`# type: ignore[no-redef]` on except-branch bare
    imports only). `cast` for object/Any values hitting type-specific ops (`xbmcvfs.translatePath`,
    track-index dict values, the `tv_control` `dict[str, Any]` call sites); a `Protocol` for the
    injected fs dep in preset_manager; local var annotations in installer's XML/keymap builders.
  - **`installer` (~958 lines)** runs `xbmcaddon.Addon()` and builds playercorefactory/keymap
    XML — annotations + no-op casts only; 15 installer tests pass; zero behavior change.
- **CI / gates (software-verified only; hardware validation not claimed):**
  `tools/type_check.py --gate` **46 files, 0 errors**; `pytest -n auto` **938 passed /
  3 skipped**; serial coverage **99.05%**; `ruff check` + `ruff format --check` clean.
- **Phase A review focus:**
  - `installer` especially: confirm signature/typing-only — no change to settings reads,
    XML generation, or the `xbmcaddon`/dialog control flow.
  - Confirm the `tv_control` `cast("dict[str, Any]", settings)` call sites are behaviour-neutral.
- **No Phase C / on-device step:** typing/allowlist only — no runtime code paths, settings,
  or hardware behavior change.
- **Rollout status:** PRs 4–7 take the gate **28 → 46**; the ENH-#51 idiom + cascade scope is
  complete. The last ungated source (`playercorefactory_merge`, top-level `service.py` /
  `default.py`) is handled by PR 8 below.

### ENH-#51 — mypy --strict allowlist expansion (PR 8 of N: the last ungated source)

- **Implementing SHA:** `fae98cb` on `claude/enh51-mypy-pr8-m3k9p2qv` (draft PR #69;
  commented on issue #51). **Stacked on PR #66** (base = the PR 7 branch); **merge
  #63 → #64 → #65 → #66 → #69 in order**, retargeting #69 to `main` before #66's branch is
  deleted to avoid the stacked-PR auto-close.
- **Scope:** the final ENH-#51 batch. Annotates the last ungated add-on source to zero strict
  errors and gates it (46 → 49): top-level `service.py` (85 errors), `default.py` (8), and
  `resources/lib/kodi/playercorefactory_merge.py` (28). After this, **no ungated
  `resources/lib` or top-level source remains** — the ENH-#51 source rollout is complete.
- **What changed (type-only, behaviour-preserving):**
  - [`mypy.ini`](../mypy.ini) + [`pyproject.toml`](../pyproject.toml) mirror: 3 modules added.
  - `service.py`: signatures on `log`/`Monitor`/`InterceptionPlayer`/`_service_main` + the
    startup-power helpers; two `no-any-return` pinned locals; `# type: ignore[misc]` on the
    conditional `xbmc.Player`/`xbmc.Monitor` base classes; `# type: ignore[attr-defined]` on
    the `oppo_control` hub re-export. `default.py`: signatures on `run_diagnostics_dashboard`
    + nested probes; `cast` on `diag.save_report`; `# type: ignore[attr-defined]` on the
    `diagnostics` hub re-export. `playercorefactory_merge.py`: signatures throughout +
    `# type: ignore[attr-defined]` on the `disc_classification` re-export.
- **CI / gates (software-verified only; hardware validation not claimed):**
  `tools/type_check.py --gate` **49 files, 0 errors**; `pytest -n auto` **938 passed /
  3 skipped**; serial coverage **99.05%** (≥ 99% floor); `ruff check` + `ruff format --check`
  clean; the pre-push hook re-ran the 99% coverage gate.
- **Phase A review focus:**
  - Confirm `service.py` is signature/typing-only — no change to the service loop, the
    `Monitor.onSettingsChanged` no-state-mutation invariant, or the startup-power control flow.
  - Confirm the two `no-any-return` pinned locals (`_translate`, `_resolve_localized`) and the
    `default.py` `cast(str, diag.save_report(...))` are behaviour-neutral pass-throughs.
- **No Phase C / on-device step:** typing/allowlist only — no runtime code paths, settings,
  or hardware behavior change.

### Add-on — hold_playback robustness: bound holds + fix verbose_push fallback (#112 / #115 / #116)

- **Implementing SHA:** `a16a4f4` on `claude/hold-robustness-a7f3c1e9` (draft PR — commented on
  issues #112, #115, #116). First of the robustness-bug session's PRs.
- **Scope:** stop `hold_playback` from pinning Kodi's playback slot (and the `oppo203iso-active`
  session sentinel) long past the end of playback. No change to playback routing, OPPO payloads,
  TV/AVR sequencing, or the idle-confirmation / definitive-stop / trick-play-suppress logic.
- **What changed (software-verified only):** `resources/lib/kodi/external_player.py`:
  - **#112** — extracted the `tcp_qpl_poll` loop into `_hold_tcp_qpl_poll(settings)` and call it
    from the `verbose_push` connect-failure path (which previously set `mode='tcp_qpl_poll'` and
    fell through *past* the QPL handler into the blind `fixed_timeout` sleep).
  - **#115** — `manual_file` is now bounded by the `fixed_timeout_minutes` ceiling (default 180)
    instead of waiting forever for a stop file that never appears.
  - **#116** — `http_poll` and `tcp_qpl_poll` end the hold after `MAX_CONSECUTIVE_POLL_FAILURES`
    (5) connection/unreachable failures instead of polling to the 240-minute timeout. A graceful
    no-response (recv timeout) still does **not** count as a failure.
  - `tests/test_hold_robustness.py` (4 tests): verbose_push fallback polls #QPL (not the fixed
    sleep); manual_file returns at the ceiling; http_poll + tcp_qpl_poll abort after 5 failures.
- **CI / gates (software-verified only; hardware validation not claimed):** `pytest` **967 passed
  / 3 skipped**; serial coverage **99%** (≥ 99% floor; new branches covered, the `external_player.py`
  misses are pre-existing); `ruff check` + `ruff format --check` (changed files) clean; mypy strict
  gate **49 files, 0 errors**.
- **Phase A review focus:** confirm `_hold_tcp_qpl_poll` is a pure extraction (idle logic
  identical); confirm the manual_file ceiling and the 5-failure abort threshold read sensibly;
  confirm no behavior change to the http_poll definitive-stop / trick-play-suppress paths.
- **Phase C — on-device:** on the real Kodi box + OPPO, exercise each hold mode and confirm the
  slot/sentinel releases near actual disc-end: (a) `verbose_push` with the OPPO refusing the push
  port → falls back to QPL polling and ends on stop; (b) `manual_file` with no stop file → ends at
  the ceiling; (c) `http_poll` / `tcp_qpl_poll` with the OPPO powered off mid-playback → ends
  within ~5 polls, not 4 hours. The abort threshold (5) and the ceiling may need tuning against
  real timing.

## Phase B — post-merge sanity

_(none queued)_

## Phase C — operator end-to-end verify

### ENH-#57 — change-scoped fast local test loop (pytest-testmon)

- **Issue / SHA:** [#57](https://github.com/skull-01/script.oppo203.iso.external/issues/57) —
  delivered by [PR #59](https://github.com/skull-01/script.oppo203.iso.external/pull/59),
  merge `9f102a3` (impl `a68ce5f`).
- **What changed:** `tools/dev_test.py` wraps `pytest --testmon` so a local run executes
  only the tests affected by changed code; `pytest-testmon>=2.2,<3` added to
  `requirements-dev.txt`; `.testmondata` git-ignored; 5 guard tests. Local-only and dormant
  unless `--testmon` is passed — CI, `scripts/verify.sh`, and the 99% coverage floor are
  unchanged.
- **Operator confirm (software only; no hardware):**
  1. `cd C:\Users\rigel\Documents\gitrepo\script.oppo203.iso.external; .venv\Scripts\python.exe tools\dev_test.py --full` — first run rebuilds the impact map (~74s, whole suite green).
  2. Re-run with no edits → `no tests ran` (everything deselected).
  3. Edit one module, re-run → only that module's dependent tests run.
  4. `git status` shows `.testmondata` ignored (never staged).

### Configurator config-write hardening — PR #68 review fixes (#72–#87) + ENH-#41 Part C

- **Issues / SHAs:** fixed across `454e5ab` (PR #68: #72, #73, #74, #75, #76, #78, #79, #80,
  #81, #82, #83, #84) and the follow-up configurator-cleanup PR (#85, #77, #86, #87, and the
  configurator side of ENH-#41 Part C — a provenance marker in the generated `settings.xml`).
- **What changed (software-verified):** merge/deploy paths never blind-overwrite user config —
  all tiers read back and merge `playercorefactory.xml` + `settings.xml`, and a malformed file
  is refused rather than replaced; the Rust SSH/probe/deploy commands validate host/user, read
  OPPO replies until CR, verify the remote backup before overwriting, and write atomically; the
  Step 3 IP-control test passes only when the player reports power `ON`; the persisted screen id
  is validated. Verified: `tsc -b` + `vite build`, **63 vitest tests**, and `cargo check` all
  green; the add-on 99% coverage gate stayed green on push.
- **Operator confirm (Phase C — on real hardware, NOT done by the agent):**
  1. **Tier B (SMB):** with an existing `playercorefactory.xml` containing your own `<player>`/
     `<rule>` entries on the Kodi box, run Apply → your entries survive and the OPPO player +
     rules are merged in; a timestamped `.bak` is left beside the file.
  2. **Tier A (SSH):** same check over SSH (key auth) → merge (not overwrite), Kodi restarts,
     and any other `settings.xml` values you had are preserved.
  3. **Malformed-file refusal:** hand-break `playercorefactory.xml`, run Apply → expect a clear
     "refusing to merge" error and the broken file left untouched (not replaced).
  4. **IP-control test:** with the player in standby, run the Step 3 wake test → it should show
     "Two-way IP control confirmed" only when the player actually powers ON.
  5. **SSH input guard:** an IP/username beginning with `-` is rejected, not passed to `ssh`.

### ENH-#103 — TV database schema v2 (296 model families) + region filtering

- **Issue / SHAs:** [#103](https://github.com/skull-01/script.oppo203.iso.external/issues/103) —
  delivered by [PR #104](https://github.com/skull-01/script.oppo203.iso.external/pull/104),
  merge `5380425` (impl `343041c`, `cde87c6`). Shipped in configurator **v0.3.0**.
- **What changed (software-verified):** `tvdb.ts` migrated to schema v2 (tier
  `preferred|fallback|probe`; `primary_backend`/`fallback_backends`/`regions`/`platform`/
  `mapping_confidence`; `parseTvDb` gates `schema_version === 2`; `modelsForRegion`). Both
  `tv-models.json` copies replaced with the 296-row 2018–2025 payload. Step 3 leads with a
  Region selector and surfaces the new fields. No add-on/Python changes.
- **Software gates (this machine):** `tsc --noEmit` clean; `vitest` **68/68**; `npm run build`
  exit 0; browser-preview pass (region filter interactive US↔Asia on Hisense; zero console errors).
- **Operator confirm (Phase C — real Windows host, NOT done by the agent):**
  1. Install configurator v0.3.0; open Step 3, pick a brand, and toggle Region — confirm the
     model list changes per market (e.g. Hisense **US** = Android TV + Roku; **Asia** = VIDAA).
  2. Confirm each row shows platform · backend · fallback · regions · confidence + a tier chip.
  3. Confirm all rows are presented as candidate (unvalidated) mappings — no hardware claim.

### ENH-#105 — canonical players DB (players.json) + configurator adoption

- **Issue / SHAs:** [#105](https://github.com/skull-01/script.oppo203.iso.external/issues/105) —
  delivered by [PR #106](https://github.com/skull-01/script.oppo203.iso.external/pull/106),
  merge `81c3eb5` (impl `4b7f63e`, `9ab2f61`, `18d423e`, `5675f70`). Shipped in configurator **v0.3.0**.
- **What changed (software-verified):** new `players.json` (bundled + docs, byte-identical)
  consolidating the 18-model player taxonomy + brand metadata + candidate regions; `playersdb.ts`
  loader + `players.ts` derives `PLAYER_BRANDS` from it; Step 2 surfaces markets/wake/class/NAS.
  Add-on side is **test-only**: a consistency guard pins the JSON to the live registries and the
  two `== 18` counts derive from the DB. `settings.xml` ordering + `hardware_presets.py` unchanged.
- **Software gates (this machine):** configurator `tsc` clean + `vitest` **74/74** + build OK;
  add-on `pytest -n auto` **950 passed / 3 skipped**, `ruff` clean, `mypy --gate` clean (52 files),
  serial coverage **99%**, `audit_release` **580/580**.
- **Operator confirm (Phase C — real Windows host, NOT done by the agent):**
  1. Open Step 2, pick brand + model — confirm the facts line shows markets, wake command,
     hardware class, and NAS-playback candidacy, and the posture callout still matches.
  2. Confirm every existing player still resolves to the same `oppo_hardware_model` value
     (the picker labels are unchanged; only the per-brand order is enum-ordered now).
  3. Add-on: nothing to verify on hardware (test-only); confirm `main` add-on still builds.

### Configurator v0.4.0 + v0.5.0 — AVR (AV Receiver) Step 5

- **PRs / SHAs:** [PR #109](https://github.com/skull-01/script.oppo203.iso.external/pull/109)
  merge `6251cdf` (v0.4.0 — AVR database + advisory Step 5),
  [PR #110](https://github.com/skull-01/script.oppo203.iso.external/pull/110) merge `bc3ad0e`
  (v0.5.0 — Step 5 wired into the add-on `settings.xml`). PR-only theme (no tracked issue), per
  the configurator's untracked-delivery pattern. Shipped in configurator **v0.5.0** (repo "Latest").
- **What changed (software-verified):** new `avr-db/avr-models.json` (224 AVR model families,
  schema v2) + `avrdb.ts` loader; optional **Step 5 (AV Receiver)** picker (ask → brand →
  region/year-filtered model list); a "Receiver control" card captures receiver IP + player input;
  `mapping.avrAddonBackend()` maps DB backends onto the add-on enum (Pioneer→`pioneer_eiscp`,
  Sony→`sony_audio_api`). Conservative enable: `avr_control_enabled` only for a native non-gated
  driver with host + input present; Sony configured-but-off; Anthem/Arcam/NAD write no `avr_backend`.
  Skipping Step 5 emits nothing AVR-related. **No add-on code change.**
- **Published-artifact integrity (agent-verified 2026-05-31):** the `configurator-v0.5.0` release
  MSI (3,174,400 B) and NSIS setup (2,071,403 B) were re-downloaded and their SHA-256 confirmed
  **byte-identical** to both the `.sha256` sidecars and `release-evidence/v0.5.0/BUILD_NOTES.md`
  (MSI `60283a0240afd0aa745a9fa5d853e125a6558572fcd269b911c90b3ab0792742`, NSIS
  `8022844316ee8c25e0463f3334d9148376fd97fec9c9f7e60f46052d4dc4a709`). Unsigned — SmartScreen
  "unknown publisher" expected.
- **Software gates (release sessions):** `tsc -b` clean; **101 vitest** (22 mapping tests);
  `npm run build` OK; Step 5 Pioneer/Sony paths exercised in a browser preview.
- **Operator confirm (Phase C — clean Windows host, NOT done by the agent):**
  1. Install from the `configurator-v0.5.0` release (NSIS `…_x64-setup.exe` or the MSI); confirm
     `Get-FileHash <file> -Algorithm SHA256` matches the BUILD_NOTES table, and that it installs
     without error past the unsigned-publisher SmartScreen prompt.
  2. Confirm the Start-menu / desktop / taskbar + window icon shows the add-on artwork (not a
     generic/blank icon), the custom title bar renders, and the wizard opens.
  3. Step 5 → "Yes" → pick a brand + model; confirm the **Receiver control** card appears with
     IP + player-input fields, and that filling both shows the green "we'll enable control" callout
     (Sony instead shows "left off — needs ack + PSK"; Anthem/Arcam/NAD show "no native backend").
  4. Regression: confirm the Step 3 Region filter and the Step 2 player facts line still behave.
  5. Run the final Apply (Tier A/B/C) and confirm the generated `…/settings.xml` carries
     `avr_backend` / `avr_host` / `avr_player_input` / `avr_control_enabled` as expected — and that
     **skipping** Step 5 leaves any existing AVR settings untouched.
  6. Uninstall via Apps & features (or the MSI) and confirm clean removal.
  - **Software-verified + published-artifact-integrity-verified only; installed-app behaviour,
    icon appearance, and Step-5 end-to-end not verified by the agent. No hardware validation.**

---

## Verified (archive)

_Move rows here after Phase C passes and the issue is closed. Newest at the top._

_(empty)_
