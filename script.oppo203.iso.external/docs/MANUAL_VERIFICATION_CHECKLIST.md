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

## Addon backlog audit + Phase-C runbook

The open `area:addon` bug/ENH backlog is already merged to `main`; what remains is your
on-device Phase C. A per-issue **audit** — confirmed-fixed evidence (`file:line` + the pinning
test) plus the exact on-device steps — lives in [`docs/audit/`](audit/README.md). Start there
for the Phase-C steps; the detailed pre-merge rows below remain the per-PR record.

- [`addon_robustness_audit.md`](audit/addon_robustness_audit.md) — #111 / #112 / #114 / #115 / #116 / #117 / #123 (robustness; merged #129–#133).
- [`addon_svm3_audit.md`](audit/addon_svm3_audit.md) — #150 / #151 / #152 + #113 verify-played (SVM3; merged #143–#145). Note: the audit flags #113 as **fully realized for SVM3, partial for legacy** — decide its disposition at Phase C.

---

## Phase A — pre-merge

### Configurator — Reset-all reachable from app header + Step 0 — #263

- **Branch / PR:** `claude/cfg-reset-all-reachable-21230273` → [PR #264](https://github.com/skull-01/script.oppo203.iso.external/pull/264) (draft). Issue [#263](https://github.com/skull-01/script.oppo203.iso.external/issues/263) (`type:bug`, UX/discoverability). Implementing SHA `285b5e3`.
- **What changed (software-verified only):** the Reset-all action previously rendered only on the Live dashboard (reachable only via `go("dashboard")` from the final test screen, after a completed setup), so a fresh/broken install could not find it. Added a `reset_all` utility screen (`configurator/src/screens/ResetAll.tsx`) that reuses `ResetAllCard` **unchanged**, surfaced from two persistent entry points: a "Reset all…" button in the app header (`App.tsx`, visible on every screen, hidden only on the reset screen itself) and a "Reset all configurations…" link on the Step 0 gate (`Step0Gate.tsx`). `steps.ts` adds `reset_all` to the `ScreenId` union + both exhaustive maps (`SCREEN_TO_STEP`→`step0`, `SCREEN_TO_CHAIN`→`media`). The dashboard card and the reset action (`reset.ts`, the Rust `reset_box_*`/`reset_app_data` commands) are untouched.
- **Software gates (this machine):** `tsc --noEmit` 0, **304 vitest** (301 prior + 3 new in `steps.test.ts` pinning the `reset_all` map wiring), `npm run build` clean. Browser-verified (vite dev): the header entry appears on Step 0 + a mid-wizard step (Step 1) and is hidden on the reset screen; both entry points navigate to the reset screen; the reused danger card reveals its confirm gate ("Yes — delete everything…" / "Cancel"); "← Back" returns to Step 0; no console errors.
- **Operator verifies (Phase C — real Windows host / Kodi box):** from a **fresh install** (no completed setup), confirm the "Reset all…" header button and the Step 0 "Reset all configurations…" link are both visible and open the reset screen; then run the actual reset and confirm it deletes the add-on + every configurator-deployed file from the box (per deployed tier) and returns the configurator to first-run. The on-box deletion path is unchanged from v0.8.2 and is **not hardware-validated** here. Ships in configurator **v0.8.4**.

### Configurator — Reset-all: no hang on unreachable devices + live progress — #266

- **Branch / PR:** `claude/cfg-reset-all-progress-9f3c1a` → [PR #267](https://github.com/skull-01/script.oppo203.iso.external/pull/267) (merged to `main`, `3d7cbe7`); bump to v0.8.5 [PR #268](https://github.com/skull-01/script.oppo203.iso.external/pull/268) (`4176d0c`). Issue [#266](https://github.com/skull-01/script.oppo203.iso.external/issues/266) (`type:bug`). Implementing SHA `511e3b0`.
- **What changed (software-verified only):** Reset-all froze the app for ~40s on a powered-off Kodi box (tier A fires five sequential `ssh` ConnectTimeout=8 calls) or on dead-SMB filesystem timeouts (tier B), and a box failure aborted the whole reset before local state was cleared (so a user whose box was gone could never reset to first-run). Now `reset_box_ssh` does a fast SSH-port-22 reachability pre-probe (`connect_timeout` 2.5s) and `reset_box_userdata` probes the SMB share (port 445) for a UNC target — both fail in seconds with a clear message instead of grinding through timeouts; `resetEverything` runs the box and local resets as **separate stages** so a box failure no longer blocks the local reset (start-over always works); `ResetAllCard` renders a live step list (pending/running/done/failed) driven by the orchestrator + a granular `reset-progress` event from Rust. The set of deleted paths is unchanged (the four configurator-owned paths, pinned by `box_reset_targets`).
- **Software gates (this machine):** `cargo test` **43** (+1 `unc_host`), `tsc -b` 0, **311 vitest** (+7 in `reset.test.ts`: `resetStepPlan` ×3, `resetEverything` stage-separation ×4), `vite build` OK. Browser-verified (vite dev): both entry points reach the ResetAll screen; clicking through renders the live "Reset progress" step list and (no Tauri runtime in vite) the local step shows `failed` with its detail + the summary message — proving the list + failure rendering and that it **does not freeze**; no console errors.
- **Operator verifies (Phase C — real Windows host / Kodi box):** with the **box powered off / unreachable**, run Reset-all and confirm it fails fast (~2.5s, not a long freeze) with a clear message and **still resets the configurator to first-run**; with the **box reachable**, confirm the live step list shows each path being removed + the Kodi restart, and the add-on + deployed files are actually deleted. The on-box deletion path is unchanged from v0.8.2 and is **not hardware-validated** here. Ships in configurator **v0.8.5**.

### Configurator — TV DB: +110 TCL/Hisense rows (2018–2026), 9 updated — PR #258

- **Branch / PR:** `claude/tv-db-tcl-hisense-2026` → [PR #258](https://github.com/skull-01/script.oppo203.iso.external/pull/258) (merged to `main`, `3507196`). Data addition from two model-research datasets; no `type:bug` filed (not a bug — file an `ENH-` if you want it tracked).
- **What changed (software-verified only):** 110 new TCL/Hisense model rows + 9 existing rows updated in place, transformed into the `lineups`+`models` schema (backend/region/lineup mapped; regions folded to US/UK/EU/Asia/CN; all `validated:false`, confidence low CN / medium global). No new lineups; every model references an existing lineup. Both bundled + docs copies byte-identical; total models 350→460.
- **Software gates (this machine):** `tsc --noEmit` 0, **297 vitest** (incl. the `tv_db_consistency` two-copy guard), `vite build` OK.
- **Operator verifies (Phase C):** in the wizard's TV step, confirm the new TCL/Hisense families surface under the right brand/region filter with a sane recommended backend (ADB for Android/Google TV, `custom_command` for VIDAA, `roku_ecp` for Roku). The 9 in-place updates (e.g. `U7A/U8A`→`U7A`+ new `U8A`; `T7K` kept separate by year) and the candidate backend/region mappings are **not hardware-validated** — fact-check before promoting any row to `validated:true`.

### Add-on — L12: distinct Samsung TV switch defaults — #256

- **Branch / PR:** `claude/l12-samsung-hdmi-defaults` → [PR #257](https://github.com/skull-01/script.oppo203.iso.external/pull/257) (merged to `main`, `feb7f53`). Issue [#256](https://github.com/skull-01/script.oppo203.iso.external/issues/256). 2026-06-02 full-audit remediation — the final finding.
- **What changed (software-verified only):** `samsung_oppo_command`/`samsung_kodi_command` defaults were identical (`samsungctl … KEY_HDMI`, which *cycles* inputs, so switching back to Kodi sent the same keypress as switching to the OPPO). Now `KEY_HDMI1` (OPPO) / `KEY_HDMI2` (Kodi) — distinct discrete keys mirroring LG's `HDMI_1`/`HDMI_2` — kept in lock-step across `resources/settings.xml` + `settings_reader.DEFAULTS` and guarded by `test_samsung_switch_defaults_are_distinct`.
- **Software gates (this machine):** `pytest -n auto` **1155/3**, mypy `--strict` **51/0**, ruff check + `ruff format --check` clean, serial coverage **99%** (gate exit 0).
- **Operator verifies (Phase C — real hardware):** on a Samsung TV, confirm `KEY_HDMI1`/`KEY_HDMI2` select the OPPO and Kodi inputs respectively, or edit to your input layout. Older Samsung sets that only accept `KEY_HDMI` (cycle) need the commands edited. **Not hardware-validated.**

### Add-on — H2 follow-up: Pure-HTTP launch fails honestly — #254

- **Branch / PR:** `claude/h2-pure-http-fail-honestly` → [PR #255](https://github.com/skull-01/script.oppo203.iso.external/pull/255) (merged to `main`, `1453a6f`). Issue [#254](https://github.com/skull-01/script.oppo203.iso.external/issues/254). 2026-06-02 full-audit remediation — the deferred High finding, now fixed.
- **What changed (software-verified only):** `external_player._start_oppo_http` no longer wraps the sequence in a blanket `try/except`; the required `activate -> signin -> play` core propagates (the wake/mount/auto-heal/confirm steps stay best-effort), so `run_playback_session` records `rc=1` / `session_state=failed` instead of silent success on the default `http_handoff` routing. Two tests flipped to assert propagation; the mount/confirm non-fatal tests are unchanged.
- **Software gates (this machine):** `pytest -n auto` **1154/3**, mypy `--strict` **51/0**, ruff check + `ruff format --check` clean, serial coverage **99%** (gate exit 0).
- **Operator verifies (Phase C — real hardware):** force a Pure-HTTP launch failure (e.g. an unreachable player IP) and confirm the status JSON / dashboard reports the session as **failed**, not stopped/success.

### Configurator — Wave C2: wizard step-number banners, controlled inputs, dead UI, naming — #246–#252

- **Branch / PR:** `claude/wave-c2-wizard-flow-naming` → [PR #253](https://github.com/skull-01/script.oppo203.iso.external/pull/253) (merged to `main`, `0276e2a`). Issues [#246](https://github.com/skull-01/script.oppo203.iso.external/issues/246)–[#252](https://github.com/skull-01/script.oppo203.iso.external/issues/252). 2026-06-02 full-audit remediation, **Wave C2**.
- **What changed (software-verified only):** **M6 (#246)** the section banners in `step2`/`step4`/`step5`/`step6.tsx` now match the `STEPS` numbers (3/5/6/7) and the dashboard "after Step 4" string is now Step 5. **M7 (#247)** the Player IP input is controlled (bound to `state.playerIp`) so it no longer desyncs from persisted state. **L5 (#248)** `deriveRewrite` normalizes `\`→`/` for segment matching (a Windows/UNC OPPO mount path yields a rewrite). **L7 (#249)** the ADB warning keys on `state.tvBackend == "adb"`. **L8 (#250)** Step0Exit's cards are non-interactive and the dead "Open setup guide" button is removed. **L14 (#251)** the decorative password field is removed (Tier-A states "SSH key (non-interactive)"). **L16 (#252)** the Pure-HTTP tile copy calls out that it switches the Kodi-box handoff to HTTP, replacing the routing picked there.
- **Software gates (this machine):** `tsc --noEmit` clean, **297 vitest**, `npm run build` OK.
- **Operator verifies (Phase C — no hardware):** open the wizard and confirm the Progress stepper numbers match the screen banners/headings; resume with a saved Player IP and confirm Step 3 shows it; confirm the Step0Exit page has no dead buttons; confirm Tier A shows "SSH key (non-interactive)" with no password field.

### Configurator — Wave C1: settings.xml secret masking, token-owned live monitor, SSH/IO hardening — #239–#244

- **Branch / PR:** `claude/wave-c1-secret-and-rust-safety` → [PR #245](https://github.com/skull-01/script.oppo203.iso.external/pull/245) (merged to `main`, `93d5151`). Issues [#239](https://github.com/skull-01/script.oppo203.iso.external/issues/239)–[#244](https://github.com/skull-01/script.oppo203.iso.external/issues/244). 2026-06-02 full-audit remediation, **Wave C1**.
- **What changed (software-verified only):** **H3 (#239)** `debug/log.ts` `maskSettingsXmlSecrets()` content-scrubs secret `<setting id="...">` values inside the deploy settings.xml blob (the redactor keyed on field name, but the blob rides under a *filename* key). **M4 (#240)** `start_oppo_live_monitor` returns an owner token; `stop_oppo_live_monitor` takes `Option<u64>` and is a no-op unless the token matches the owner — each frontend subscriber (dashboard, SVM3 card, self-test) tracks its own token, so a sibling screen's unmount can't cancel another's stream. **L9 (#243)** the monitor lock recovers from poison. **M8 (#241)** SSH `ServerAliveInterval=5`/`ServerAliveCountMax=3` keepalive bounds a hung connection + a 64 KiB cap on `oppo_http_exchange`. **L6 (#242)** `deploy_to_userdata` + `deploy_ssh` roll the whole file set back on a mid-loop failure. **L3 (#244)** `reveal_path` validates an existing absolute path before spawning Explorer.
- **Software gates (this machine):** `tsc --noEmit` clean, **296 vitest**, `npm run build` OK, `cargo test` **40/0**, `cargo fmt --check` clean.
- **Operator verifies (Phase C):** (H3) open the debug panel (Ctrl+Shift+D), run an Apply, confirm the captured settings.xml shows `[redacted]` for `sony_psk` / `sony_avr_psk` / `smartthings_token`. (M4 — needs a real OPPO) with the dashboard streaming, open + close the SVM3 card / self-test and confirm the dashboard stream is **not** torn down, and that manual Stop still stops. (M8/L6/L3) an SSH deploy to an unreachable box is bounded (not hung); a partial-failure deploy rolls back.

### Add-on — Wave A3: configurator-owned settings declared, AVR-id guard, preset comments — #235 #236 #237

- **Branch / PR:** `claude/wave-a3-schema-guards` → [PR #238](https://github.com/skull-01/script.oppo203.iso.external/pull/238) (merged to `main`, `29778cb`). Issues [#235](https://github.com/skull-01/script.oppo203.iso.external/issues/235) / [#236](https://github.com/skull-01/script.oppo203.iso.external/issues/236) / [#237](https://github.com/skull-01/script.oppo203.iso.external/issues/237). 2026-06-02 full-audit remediation, **Wave A3**.
- **What changed (software-verified only):** **M3 (#235)** the 9 configurator-emitted architecture/HDMI/HTTP keys are declared as hidden (`visible="false"`) settings in `resources/settings.xml` (count 99→108) so a Kodi settings-GUI save preserves them instead of regenerating settings.xml and dropping them; the 5 timing keys are added to `DEFAULTS` (+ `hdmi_switch_mode` to `ENUM_VALUES`); `playback_architecture_preset` deliberately stays out of `DEFAULTS` so its empty value keeps driving the `normalize_architecture` back-fill. **L11 (#236)** a new guard pins the two `avr-models.json` copies identical and asserts every declared backend (except the intentional no-native `custom_command`) maps via `normalize_avr_backend` to a known `avr_backend` enum. **L15 (#237)** "six"→"seven" preset comments in `settings_reader.py` + `playback_session.py`.
- **Software gates (this machine):** `pytest -n auto` **1153/3**, mypy `--strict` **51/0**, ruff check + `ruff format --check` clean, serial coverage **99%** (gate exit 0).
- **Operator verifies (Phase C — no hardware):** open the add-on's Settings in Kodi and **Save**, then confirm the configurator-written `playback_architecture` / `playback_architecture_preset` / HDMI-timing values in `addon_data/script.oppo203.iso.external/settings.xml` are **preserved** (not reverted to defaults).

### Add-on — Wave A2: SVM3 monitor truth, OPPO/eISCP read robustness, clone wake, TV switch — #226–#233

- **Branch / PR:** `claude/wave-a2-monitor-transport` → [PR #234](https://github.com/skull-01/script.oppo203.iso.external/pull/234) (merged to `main`, `374b4ff`). Issues [#226](https://github.com/skull-01/script.oppo203.iso.external/issues/226)–[#233](https://github.com/skull-01/script.oppo203.iso.external/issues/233). 2026-06-02 full-audit remediation, **Wave A2**.
- **What changed (software-verified only):** **H4 (#226)** SVM3 `last_event_at` is set only by `@UPL`/`@UTC` playback-status pushes (not `@UVO`/`@UAU` chatter), so a never-playing-but-chatty device hits the 30 s startup-timeout instead of the 4 h session timeout. **M2 (#227)** `oppo_control._recv_line` (CR/LF reassembly) + `avr_onkyo_eiscp._recv_eiscp_frame` (header-then-data) tolerate a reply split across `recv()` segments. **M5 (#228)** `tv_adb_control.switch_input` resolves `adb_connect_before_switch` with `.get` + a local truthy check, so the diagnostics live-test path (a plain dict) no longer `AttributeError`s. **M9 (#229)** the clone wake resolvers import `hardware_profile` package-relative-first (`..kodi.settings_reader`) so `#PON`→`#EJT` is not silently disabled in the package runtime. **L1 (#230)** SVM3 `LOADING` is a keep-alive label that does not set `confirmed_playback`. **L2 (#231)** a svm3/http session that drops to the legacy hold is marked `fell_back_to_legacy_hold` in `oppo203iso-status.json`. **L10 (#232)** `OppoTcpClient.last_stop_outcome` distinguishes stopped/timeout/disconnected/connect_failed. **L13 (#233)** `_run_external` falls back to a literal `{tv_ip}` replace when a template carries stray braces.
- **Software gates (this machine):** `pytest -n auto` **1149/3**, mypy `--strict` **51/0**, ruff check + `ruff format --check` clean, serial coverage **99%** (gate exit 0). All seven presets still exercised (`test_playback_session_modes` / `test_architecture_presets`).
- **Operator verifies (Phase C — real hardware):** on a real OPPO/AVR/TV — (H4) a disc that fails to play but emits verbose chatter ends at ~30 s, not 4 h; (M2) a fragmented reply still parses; (M5) the ADB "Test switch to OPPO" diagnostic succeeds; (M9) a Chinoppo/clone wakes via `#EJT`; (L1) `confirmed_playback` is true only once the disc really plays; (L2) the dashboard shows the fall-back marker; (L10/L13) hold-timeout vs disconnect and odd TV templates behave. **Not hardware-validated.**

### Add-on — Wave A1: AVR http_handoff eligibility, HTTP path translation, settle delay — #221 #222 #223 #224

- **Branch / PR:** `claude/wave-a1-pure-http-correctness` → [PR #225](https://github.com/skull-01/script.oppo203.iso.external/pull/225) (merged to `main`, `50aa81e`). Issues [#221](https://github.com/skull-01/script.oppo203.iso.external/issues/221) / [#222](https://github.com/skull-01/script.oppo203.iso.external/issues/222) / [#223](https://github.com/skull-01/script.oppo203.iso.external/issues/223) / [#224](https://github.com/skull-01/script.oppo203.iso.external/issues/224). 2026-06-02 full-audit remediation, **Wave A1**.
- **What changed (software-verified only):** **H1 (#221)** `avr_sequence.eligible_for_external_player_avr_sequence` now accepts `{external_player, http_handoff}` (was `external_player` only), so AVR power-on/input/restore run under the Pure-HTTP default; `service_interception` stays excluded. **M1 (#222)** new `oppo_control._apply_path_rewrite` does an anchored (prefix-only) `oppo_http_path_from→to` rewrite **inside** `resolve_disc_play_path`, before the disc-folder/`checkfolderhasBDMV` decision, so the probe + returned path are in the player's mount namespace (the two payload builders no longer double-translate). **M10 (#223)** `_settle_after_power_on` (setting `avr_power_on_settle_seconds`, default 1.5s) waits between a real AVR power-on and input-select. **L4 (#224)** dropped `\` from the URL-encode safe set so backslashes percent-encode.
- **Software gates (this machine):** `pytest -n auto` **1139/3**, mypy `--strict` **51/0**, ruff check + `ruff format --check` clean, serial coverage **99%** (gate exit 0). Six prior presets unaffected (7-preset guards green).
- **Operator verifies (Phase A):** confirm the default `external_player` AVR path is unchanged and only `service_interception` is excluded; confirm the anchored rewrite matches your `oppo_http_path_from/to` (a non-prefix `from` now no-ops instead of replacing mid-path).
- **Operator verifies (Phase C — real hardware):** on a real receiver under a Pure-HTTP (`http_handoff`) install, confirm the AVR powers on + selects the player input + restores on exit, that the ~1.5s settle avoids a dropped input, and that a NAS BDMV folder with a configured path translation plays via the translated path. **Not hardware-validated.**

### Add-on + configurator — selectable confirm-gated HDMI switching (Xnoppo V3, PR5 of 6) — #217

- **Branch / PR:** `claude/pr5-hdmi-sequencing-d8008ab6` → PR (base `main`). Issue [#217](https://github.com/skull-01/script.oppo203.iso.external/issues/217).
- **What changed (software-verified only):** new `resources/lib/kodi/hdmi_sequencing.py` (pure policy: `switch_mode`/`compute_play_delay`/`av_stagger`) gated into the shared TV-switch path via `external_player._sequence_switch_and_play` (both `fast_start` and `fast_start_http`). `hdmi_switch_mode = immediate` (**default, frozen** — TV-first order, pinned byte-identical by `test_build18_external_player_order_keeps_tv_first_then_avr_then_oppo`); `delayed` starts the player first, waits `play_delay_hdmi` (≥6s for ISO/BDMV) before switching the TV, then staggers by `av_delay_hdmi`. New settings `hdmi_switch_mode`/`play_delay_hdmi`/`av_delay_hdmi` emitted by the configurator. New `tests/test_hdmi_sequencing.py` + ordering tests.
- **Software gates (this machine):** `pytest -n auto` **1132/3**, mypy `--strict` **51/0**, ruff + `ruff format --check` clean, serial coverage **99%** (gate exit 0); configurator `tsc --noEmit` 0 + **294 vitest** + `vite build`.
- **Operator verifies (Phase A):** confirm the default `immediate` path is byte-identical to today (the build18 order guard) and the `delayed` mode reorders to player-first + the disc 6s floor.
- **Operator verifies (Phase C — real hardware):** on a real TV/AVR, confirm `delayed` switches the TV only after the player is rendering (no black-screen flash) and the disc floor / AVR stagger feel right — **not hardware-validated**.

### Configurator — default flip to Pure HTTP + process-monitor transport + docs (Xnoppo V3, PR4 of 6) — #215

- **Branch / PR:** `claude/pr4-default-flip-bc26c98d` → PR (base `main`). Issue [#215](https://github.com/skull-01/script.oppo203.iso.external/issues/215).
- **What changed (software-verified only):** new installs now **default to Pure HTTP** (`INITIAL_STATE.monitorMode = "http"` → preset `http_handoff_http`); the Step-3 player test records SVM3 support without overriding an explicit `http` choice; Step-4 copy updated (Pure HTTP = recommended). New **Refresh Rate** setting `oppoHttpRefreshSeconds` (default 5) emitted as `oppo_http_refresh_seconds`. The dashboard **process-monitor transport** follows the Step-4 choice: a Pure-HTTP install probes the player over HTTP/436 (`oppo_playback_info`) instead of TCP `#QPW` (new `oppo-http` liveness kind). **No add-on code change** — `normalize_architecture` already derives legacy for pre-preset (existing) installs, so existing installs are unaffected; only new installs get the http preset. Docs: `BUILD_PLAN.md` D-A → `http_handoff_http`, `AGENTS.md` norm updated to the seven-preset asymmetric matrix.
- **Software gates (this machine):** configurator `tsc --noEmit` 0 + **293 vitest** + `vite build`; **browser-verified** (vite dev server): a fresh wizard's Step-4 shows **Pure HTTP selected by default** with "recommended for new installs", SVM3 reads "TCP verbose-mode confirmation", and the callout says "Pure HTTP is the default". **Add-on `resources/` untouched → suite stays 1124/3.**
- **Operator verifies (Phase A):** confirm the default flip is what you want (new installs → undocumented HTTP path); confirm existing installs (with a stored preset / pre-preset legacy) are unchanged.
- **Operator verifies (Phase C — real hardware):** on a fresh install against a real OPPO, confirm Pure HTTP plays + the dashboard's HTTP liveness probe reflects reachability — **not hardware-validated**.

### Add-on + configurator — checkfolderhasBDMV-first disc nav (Xnoppo V3, PR6 of 6) — #213

- **Branch / PR:** `claude/pr6-tcp-bdmv-3db2d167` → PR (base `main`). Issue [#213](https://github.com/skull-01/script.oppo203.iso.external/issues/213).
- **What changed (software-verified only):** new `oppo_control.resolve_disc_play_path(settings, media_file)` is the shared disc-folder resolver used by `_translate_media_path` + `_build_json_payload` (so it covers the http_handoff routing AND the TCP `http_api`/`tcp_then_http` modes). **Off path is byte-identical to today's `_disc_folder_root`**; when `oppo_bdmv_checkfolder` is on AND `supports_http(model)`, a BDMV marker is confirmed via `/checkfolderhasBDMV` before the folder root is used — no-BDMV → original marker; toggle-off / not-capable / unreachable all fall back to the folder root. PR3's redundant logging probe in `_http_play_disc_aware` is consolidated here. Configurator: `oppoBdmvCheckfolder` state (default on) emitted as `oppo_bdmv_checkfolder` for http_handoff (mirrors `oppo_http_disc_folder_root`, no dedicated UI). New `tests/test_oppo_bdmv_checkfolder.py` + `mapping.test.ts` pin.
- **Software gates (this machine):** `pytest -n auto` **1124/3**, mypy `--strict` **51/0**, ruff + `ruff format --check` clean, serial coverage **99%** (gate exit 0); configurator `tsc --noEmit` 0 + **292 vitest** + `vite build`.
- **Operator verifies (Phase A):** read `resolve_disc_play_path` — confirm every fallback branch returns the folder root (frozen) and only a capable+reachable+no-BDMV verdict returns the original marker. Confirm `oppo_http_disc_folder_root`/`oppo_bdmv_checkfolder` off paths are unchanged.
- **Operator verifies (Phase C — real hardware):** on a real OPPO with a BDMV disc, confirm `/checkfolderhasBDMV` returns the expected verdict and the resulting play path is correct — **not hardware-validated**.

### Add-on — pure-HTTP launch orchestration: mount + ISO auto-heal + BDMV probe (Xnoppo V3, PR3 of 6) — #211

- **Branch / PR:** `claude/pr3-http-orchestration-169e6c9a` → PR (base `main`). Issue [#211](https://github.com/skull-01/script.oppo203.iso.external/issues/211).
- **What changed (software-verified only):** `external_player._start_oppo_http` (the http_handoff launch) goes from `activate→signin→play` to the full Xnoppo flow — wake (`send_remote_key_http("PON")`), signin, **best-effort mount** (parse `smb://`/`nfs://` from the media path → `detect_nfs`-routed `login_*`+`mount_*`; skipped for non-network paths), **disc-aware play** (BDMV path → `checkfolderhasBDMV` probe logged; **ISO → one-shot auto-heal**: resend once if not confirmed playing after `oppo_http_iso_autoheal_after_seconds`=20 when `oppo_http_iso_autoheal`=on), then a `getglobalinfo` confirm. **Every step beyond activate→signin→play is best-effort + non-fatal**, so the path degrades to today's behaviour. New `tests/test_oppo_http_orchestration.py` (13 tests); `_patch_http` extended for the new primitives. No configurator change.
- **Software gates (this machine):** `pytest -n auto` **1113/3**, mypy `--strict` **51/0**, ruff + `ruff format --check` clean, serial coverage **99%** (gate exit 0; caught + fixed a serial-only monkeypatch-target flake by patching the exact `_oppo_control_module()` object).
- **Operator verifies (Phase A):** read the orchestration in `_start_oppo_http` + helpers; confirm every enrichment step is wrapped non-fatal and the play itself is unchanged (`play_media_http_api`).
- **Operator verifies (Phase C — real hardware):** on a real OPPO/NAS with the Pure-HTTP preset, confirm the share mounts, an ISO that drops re-heals, and `getglobalinfo` confirms — **not hardware-validated** (community-reverse-engineered endpoints; adjust strings if firmware differs).

### Add-on + configurator — 7th preset http_handoff_http + HTTP monitor (Xnoppo V3 adoption, PR2 of 6) — #209

- **Branch / PR:** `claude/pr2-http-preset-8ebbb6d2` → PR (base `main`). Issue [#209](https://github.com/skull-01/script.oppo203.iso.external/issues/209).
- **What changed (software-verified only):** the playback-preset matrix goes 6 → **7** with the asymmetric cell `http_handoff_http` (the `http` monitor exists only for the `http_handoff` routing). Add-on: `settings_reader` gains the `http` monitor mode + the 7th preset + a clamp (`architecture_preset`/`normalize_architecture` route any other `(routing,"http")` to that routing's legacy preset); new `playback_monitor_http.py` (`OppoHttpPlaybackMonitor` polls `/getglobalinfo`+`/getplayingtime`, fallback-safe) wired into `_dispatch_monitor`. Configurator: `MonitorMode |= "http"`, a **"Pure HTTP"** pill on Step 4 sets both axes, shared `playback-presets.json` + `presetsdb.ts` → 7. Cross-area matrix pinned by `test_playback_presets_consistency.py` / `test_architecture_presets.py` / `mapping.test.ts` / `presetsdb.test.ts` (all updated for the asymmetric 7th). **Default unchanged** (still `http_handoff_svm3`; PR4 flips it).
- **Software gates (this machine):** `pytest -n auto` **1100/3**, mypy `--strict` **51/0**, ruff + `ruff format --check` clean, serial coverage **99%** (gate exit 0); configurator `tsc --noEmit` 0 + **291 vitest** + `vite build`. **Browser-verified** (vite dev server): the Step-4 Playback-mode screen shows the new **Pure HTTP** tile alongside SVM3/Legacy, and clicking it selects it (the others deselect).
- **Operator verifies (Phase A):** read the clamp in `architecture_preset`/`normalize_architecture`, the new monitor module, and the Pure HTTP pill (sets both `monitorMode` + `playbackArchitecture`). Confirm the 3-place matrix (Python registries + JSON + presetsdb) agrees.
- **Operator verifies (Phase C — real hardware):** with the Pure HTTP preset selected, confirm on a real OPPO that `/getglobalinfo` reports playback and `/getplayingtime` advances so the monitor confirms — **not hardware-validated** (community-reverse-engineered API).

### Add-on — pure-HTTP/436 OPPO primitives (Xnoppo V3 adoption, PR1 of 6) — #207

- **Branch / PR:** `claude/http-primitives-b58647f2` → PR (base `main`). Issue [#207](https://github.com/skull-01/script.oppo203.iso.external/issues/207).
- **What changed (software-verified only):** adds community-reverse-engineered pure-HTTP/436 primitives to `resources/lib/oppo/oppo_control.py` (Xnoppo Elite V3 / emby-chinoppo-bridge model): `send_remote_key_http`, `get_global_info`/`global_info_is_playing`, `get_playing_time`, `get_device_list`, `detect_nfs`, `login_smb`/`login_nfs`, `list_smb_shares`/`list_nfs_shares`, `mount_smb`/`mount_nfs` (leading-slash stripped, no unmount-first), `check_folder_has_bdmv`. **Function-only / unwired** — nothing calls them yet (PR3 wires the launch orchestration). Every transport failure raises `OppoError`. New `tests/test_oppo_http_pure.py` (mocked `urlopen`).
- **Software gates (this machine):** `pytest -n auto` **1081 passed / 3 skipped** (+28), `ruff check` + `ruff format --check` clean, mypy `--strict` **51/0**, serial coverage **99%** (gate exit 0).
- **Operator verifies (Phase A):** read the new primitives + `test_oppo_http_pure.py`; confirm they are unwired (no caller) and additive.
- **Operator verifies (Phase C — real hardware):** the **endpoint paths/params are not hardware-validated**. When PR3 wires them, confirm on a real OPPO/NAS that `/sendremotekey`, `/getglobalinfo`, `/getplayingtime`, the SMB/NFS login+mount endpoints, and `/checkfolderhasBDMV` are the player's actual API (adjust the endpoint strings if firmware differs).

### Configurator — TV DB China models (CN region) + tv_ip comment fix (PR-only)

- **Branch / PR:** `claude/cfg-tvdb-china-695795c6` → draft PR (base `main`). PR-only theme (no tracked issue).
- **What changed (software-verified only):** (1) **TV DB expanded 324 → 350 model families** with **26 China-domestic** TCL + Hisense families under a **new `CN` region**: 2 new lineups (`tcl-china-android` = Android/雷鸟系统 → `adb`; `hisense-china-vidaa` = VIDAA/聚好看 → `custom_command`), 13 TCL rows (incl. the FFALCON/雷鸟 sub-brand) + 13 Hisense rows (U7/U8/E ULED families). `tvdb.ts` `TvRegion` + `TV_REGIONS` gain `"CN"`; the Step-5 region picker auto-renders the new pill. `scope.regions` + `region_schema.allowed_values` gain `CN`; `db_version` → `2026.06.02`. **All rows `validated:false`, `mapping_confidence:"low"`** — China-market OS variants gate ADB differently and have no first-class VIDAA backend, so the control paths are research candidates, not validated. Both `tv-models.json` copies kept byte-identical (`tv_db_consistency.test.ts`). (2) Fixed a stale comment in `mapping.ts wizardStateToAddonSettings` that said `tv_ip` is "not yet captured" — it IS emitted (since #198/#199).
- **Software gates (this machine):** `tsc --noEmit` 0 · `vitest` **263** (+2 CN region tests; `tv_db_consistency` byte-identical green) · `vite build`. **Browser-verified** (vite dev server): the Step-5 TV picker shows a **CN** region pill; selecting it lists all 13 China TCL families (incl. 雷鸟 鹏 7 Pro) with `Android (China) / 雷鸟系统 · adb · CN · low confidence`. No add-on change.
- **Operator verifies (Phase A):** confirm the 26 rows are reasonable China model families and the brand/OS/backend mapping (Android→adb, VIDAA→custom_command) is sane; confirm all are `validated:false`.
- **Operator verifies (Phase C — real hardware):** on a real China-domestic TCL (雷鸟系统) or Hisense (VIDAA/聚好看) set, confirm whether ADB-over-network (TCL) or a custom command (Hisense VIDAA) actually switches the HDMI input — these are **low-confidence candidates, not hardware-validated**.

### Configurator + add-on — shared playback-preset source (cross-language matrix guard; PR-only)

- **Branch / PR:** `claude/shared-preset-source-7262b0b2` → draft PR (base `main`). PR-only theme (no tracked issue) — the optional hardening flagged in `docs/BUILD_PLAN.md` §6.
- **What changed (software-verified only):** the six-option playback-preset matrix now has a single cross-language source of truth — `configurator/src/presets-db/playback-presets.json` (routing/monitor modes, the 6 presets in add-on order, `preset_by_axes`, `routing_aliases`). A new add-on guard `tests/test_playback_presets_consistency.py` pins the JSON to `settings_reader`'s `PLAYBACK_ROUTING_MODES` / `PLAYBACK_MONITOR_MODES` / `PLAYBACK_ARCHITECTURE_PRESETS` / `_PRESET_BY_AXES` / `_ROUTING_ALIASES`; a new `presetsdb.ts` loader + `presetsdb.test.ts` pin the TS side; and `mapping.test.ts`'s `CANONICAL_SIX` now **derives from the shared DB** (the manual mirror is gone). **No runtime change** — `settings_reader` keeps its tuples and `mapping.ts` its emission; the JSON is the asserted-equal source. Cross-language preset drift now fails a test instead of relying on the AGENTS.md norm + reviewer.
- **Software gates (this machine):** add-on `pytest -n auto` **1053 passed / 3 skipped** (+7 parity guard), `ruff check .` clean (new guard `ruff format`-clean); configurator `tsc --noEmit` 0 + `vitest` **266** (+5 `presetsdb`) + `vite build`. mypy / serial-coverage unaffected (no `resources/` production code changed).
- **Operator verifies (Phase A):** read `playback-presets.json` + `test_playback_presets_consistency.py` (the JSON equals the add-on tuples), `presetsdb.ts` + `presetsdb.test.ts`, and the `mapping.test.ts` `CANONICAL_SIX` now sourced from `PLAYBACK_PRESETS`. No hardware step — pure data + tests, so there is no Phase C.

### Configurator — Dashboard session-history card (issue #168; stacked on PR #201)

- **Stacked draft:** appdata store #200 → snapshot diff #201 → this session-log PR (base = the #201 branch). Rebuilds the superseded draft #166 on the current dashboard; tracks ENH #168.
- **What changed (software-verified only):** the Live dashboard gains a **Session history** card. Because the add-on overwrites its single `oppo203iso-status.json` per run, each 6s poll folds the freshly-read status into a local history (new pure `session_log.ts` `foldObservation`), persisted under appdata via PR #200's store, so past sessions survive reopening the dashboard. `foldObservation` updates the newest entry in place as a session advances `starting → stopped` (and on a heartbeat that only refreshes `updatedAt`/`phase`), opens a new entry on a signature change, caps to the newest 50, and returns the same array reference when unchanged (no persist on idle polls). **No add-on change; no Rust change; no new dependency.**
- **Exact dedup now (the 5.1 unlock):** `sessionSignature` prefers the add-on's `session_id` (shipped in add-on PR #183 / Phase 5.1, surfaced by `parseOppoStatus`) for an **exact** match, so two identical back-to-back sessions are told apart. Older records with no id fall back to the descriptor heuristic (the documented limitation #168 noted).
- **Software gates (this machine):** `tsc --noEmit` 0 · `vitest` **283** (+10 session_log) · `vite build` exit 0 · dev-server boot smoke test (app mounts, zero console errors). The live render with real sessions is Phase C.
- **Operator verifies (Phase A):** read `session_log.ts` + its 10 tests (in-place advance start→stop; same-ref-on-no-change; new entry on id-less replay / signature change; cap eviction; `session_id` exact dedup → distinct ids give distinct entries; heartbeat fold on the same id), and the `SessionHistoryCard` + the in-poll fold/persist in `screens/dashboard.tsx` (persist fires only on a real change).
- **Operator verifies (Phase C — built app + real box):** with a tier A/B deployment, play several sessions through the add-on with the dashboard open; confirm each appears in Session history with the right state / flags, that a start→stop updates one entry (not two), that a fresh session (new `session_id`) adds a new entry, then close + reopen the dashboard and confirm the history persisted (`…\dashboard\session-log.json`). **Not hardware-validated.**

### Configurator — Dashboard settings-snapshot diff card (issue #167; stacked on PR #200)

- **Stacked draft:** appdata-store PR #200 → this snapshot-diff PR (base = the #200 branch). Rebuilds the superseded draft #165 on the current (Phase 5.2/5.3) dashboard; tracks ENH #167.
- **What changed (software-verified only):** the Live dashboard gains a **Configuration changes** card. A **Snapshot now** button reads the box's `settings.xml` over the existing tier-aware routing (new shared `fileReadPlan(state, rel)`, factored from `statusReadPlan` — identical behaviour), parses it (new exported `parseSettingsXml`, factored from `mergeSettingsXml` — identical behaviour), **masks secret-bearing ids** (Sony PSK / SmartThings token / `sony_avr_psk` → a fixed `[secret]` via the shared `debug/log.ts isSensitiveKey`) **before** the snapshot is persisted AND diffed, persists the sanitized snapshot under appdata (via PR #200's store), then diffs it against the prior snapshot (added / removed / changed; the first capture is a baseline). New `settings_diff.ts` / `dashboard_snapshot.ts`. **No add-on change; no new crate dependency.**
- **Software gates (this machine):** `tsc --noEmit` 0 · `vitest` **273** (+12: settings_diff 5, parseSettingsXml 4, fileReadPlan 3) · `vite build` exit 0 · dev-server boot smoke test (app mounts, zero console errors). The live card render with a real diff needs the built Tauri app + a tier A/B box (Phase C).
- **Operator verifies (Phase A):** read `parseSettingsXml` / `mergeSettingsXml` (confirm the merge output **and** the malformed-refusal `/refusing to overwrite/` are unchanged — pinned by `settings_xml.test.ts`), `fileReadPlan` / `statusReadPlan` (tier A/B/C routing unchanged — pinned by `dashboard_status.test.ts`), `settings_diff.ts` (`sanitizeSettings` masks the 3 secret ids; a changed secret reads as no-change; `diffSettings` sorts ids), and the `SettingsDiffCard` in `screens/dashboard.tsx`.
- **Operator verifies (Phase C — built app + real box):** with a tier A/B deployment, open **Live dashboard → Snapshot now** (baseline), change a setting on the box (re-run Apply, or edit in Kodi), then **Snapshot now** again and confirm the card lists the change. Confirm a secret-bearing setting (e.g. Sony PSK) shows only its key with the value masked, and that the on-disk `…\dashboard\settings-snapshot.json` contains `[secret]`, never the real PSK/token. **Not hardware-validated.**

### Configurator — full TV-backend config persistence (PR #198, issue #199; merged to `main`)

**Software-verified only — hardware-pending.** `mapping.ts` previously persisted only Roku keys + Sony Bravia HDMI ports, so the add-on couldn't drive the other TV backends after setup. `wizardStateToAddonSettings` now emits each backend's full runtime config (value-guarded, per selected backend): `sony_psk`; the two `*_input_adb_shell` keyevents derived from the HDMI numbers; the verbatim `lg_/samsung_/custom_oppo_command`+`_kodi_command` `{tv_ip}` templates; and the 5 `smartthings_*` settings (token/device/oppo+kodi input ids + `experimental_acknowledged` gated on all four). New persisted Step-5 fields; the SmartThings token is `type=password` + redactor-masked. Add-on untouched (it already reads these keys). Gate: `tsc` / **261 vitest** / `vite build`. *Phase C:* configure each TV backend (Sony Bravia PSK, adb, an LG/Samsung/custom command, SmartThings token+device+inputs), apply, and confirm the add-on drives the switch on real hardware; confirm the token never appears in the debug panel / settings snapshot.

### Configurator — Phases 3/4/5 UI layer (this session; built by 3 parallel sub-agents, merged to `main`)

All **software-verified only — hardware-pending** (no real Kodi/OPPO/TV/AVR reachable). Combined-`main` gate green: `tsc` / **247 vitest** / `vite build` / `cargo fmt` + **37 cargo tests** / zero warnings. Each wires the backend commands merged earlier this session (Phases 3.1/4.1/5.1). Frozen contracts (`mapping.ts` enums, the six presets, `playback_session`) untouched.

- **3.2 switch-and-verify** (PR #184 `c54bcb6`, issue #191): step5 real Test-switch dispatching to `tv_switch_*`/`avr_switch_*` by state; SmartThings builds-and-displays; honest manual fallback. *Phase C:* with a real TV/AVR, run Test and confirm the input actually changes.
- **3.3 auto-find inputs** (PR #188 `81b3405`, issue #192): Scan (`tv_port_probe`/`oppo_query`) + driven HDMI sweep with user confirm; replaced the fabricated-value stub. *Phase C:* confirm the sweep lands the right input on real hardware.
- **4.2 test-ISO copy** (PR #185 `a0e9eb1`, issue #193): Rust `copy_to_share` (1 MiB chunks, `copy-progress` events, temp-then-rename) + `test.tsx` source/dest/progress UI (D-2 user-supplies). *Phase C:* copy a real ISO to the share; confirm progress + integrity + the OPPO sees it.
- **4.3 live SVM3** (PR #187 `c4a97e0`, issue #194): `svm3_confirm` folds `oppo-live` (UPL PLAY → playback, advancing UTC → progress); read-only card. *Phase C:* play on a real OPPO; confirm the badges light from real frames.
- **4.4 self-test orchestration** (PR #190 `b0e590d`, issue #195): power-cycle → `oppo_http_play` (rewritten path) → SVM3-confirm → control-forward; per-step ok/fail/skipped. *Phase C:* run the whole self-test end-to-end on real hardware.
- **5.2 dashboard consume + TV liveness + auto-start** (PR #186 `1e3fec3`, issue #196): `parseOppoStatus` reads `session_id`/`started_at`/`updated_at`/`phase`; lifecycle/age/staleness; auto-start live stream (dual-subscriber guard intact); TV liveness. *Phase C:* open the dashboard during a real session; confirm phase/age + TV liveness; confirm no secret leaks. **Deferred:** `session_id` exact-dedup in `session_log.ts` (that file is not on `main` — only draft #166).
- **5.3 full-chain view** (PR #189 `824cc29`, issue #197): `chainNodeViews` topology-ordered Kodi/OPPO/TV/AVR liveness + activity; `ChainCard`. *Phase C:* confirm every node's liveness/activity against the real chain.

### Add-on — richer session status (session_id/started_at/phase) (Phase 5.1) (PR #183, issue #182)

- **Merged to `main`** (operator chose "merge to main as I go"). Branch `claude/addon-live-status-6b2f9c33`, base `main`. Implementing SHA: `332c0ba`. Tracks **#182**. **Add-on (`resources/`) change** — ships on the next configurator build (D-1=C bundles `main` fresh); no separate add-on release.
- **What changed (software-verified only):** `resources/lib/kodi/playback_session.py` now writes a richer `oppo203iso-status.json`: `session_id` (random, **stable across one session's writes** — the identity #166/#168 dedup wanted), `started_at`/`updated_at` epoch timestamps, and a `phase` field (`launching` → `monitoring` → `ended`) with a new **mid-session "monitoring" write** after the OPPO launch (previously only start + end were written). New fields are optional → the existing configurator `parseOppoStatus` is unaffected until Phase 5.2 consumes them. Gate: **pytest 1046/3**, **mypy --strict 51/0**, **ruff check + format clean**, **coverage 99%** (`playback_session.py` **100%**).
- **Operator verifies (Phase A):** read the `playback_session.py` diff (the `write` closure + `_now`/`_new_session_id` + the `phase` progression) and `test_status_carries_session_identity_and_phases`; confirm the new keys are additive and the three writes share one `session_id`/`started_at`.
- **Operator verifies (Phase C — built add-on + real session):** run a real OPPO playback session and confirm `oppo203iso-status.json` carries a stable `session_id`, advancing `updated_at`, and the `launching`→`monitoring`→`ended` phases. **Not hardware-validated.**

### Configurator — OPPO power-cycle command (Phase 4.1) (PR #181, issue #180)

- **Merged to `main`** (operator chose "merge to main as I go"). Branch `claude/cfg-oppo-power-5d8c1a90`, base `main`. Implementing SHA: `0b5a8f1`. Tracks **#180**.
- **What changed (software-verified only):** new `oppo_power` `#[tauri::command]` in `lib.rs` — the power-cycle primitive the Phase 4 self-test needs (the activate/signin/play start sequence already shipped in #174's `oppo_http_play`). Pure `oppo_power_token` maps `off`/`on`/`eject` → `#POF`/`#PON`/`#EJT` (clones lacking `#PON`, per `hardware_presets.py`); `oppo_power` delegates to `oppo_query` so it shares the CR-terminated send + the `debug-wire` transcript. Gate: **cargo 35** (1 new token test) / `cargo fmt --check` clean / **zero build warnings**. No new crate; `resources/` untouched.
- **Operator verifies (Phase A):** read `oppo_power_token` + `oppo_power` and the 1 cargo test; confirm the tokens match `hardware_presets.py` and that it reuses `oppo_query` rather than re-implementing the socket loop.
- **Operator verifies (Phase C — built app + real OPPO):** invoke `oppo_power` with `off` then `on` (or `eject` for a clone) and confirm the player actually powers down/up. **Not hardware-validated.**

### Configurator — TV input-switch commands (Phase 3.1) (PR #179, issue #178)

- **Merged to `main`** (operator chose "merge to main as I go"). Branch `claude/cfg-tv-switch-7e2b9c44`, base `main`. Implementing SHA: `9aa9e1c`. Tracks **#178**.
- **What changed (software-verified only):** per-backend TV input-switch paths in `lib.rs`, mirroring `resources/lib/tv/` (complements the existing Roku `tv_switch_roku`). `tv_switch_sony_bravia` fires `setPlayContent extInput:hdmi?port=N` POST to `/sony/avContent` with `X-Auth-PSK` directly over HTTP; `tv_switch_adb` and `tv_switch_external` run the add-on's on-box command (`adb connect`+`adb shell`, or the `{tv_ip}`-templated lg/samsung/custom command) **on the Kodi box over the existing SSH channel** (`run_ssh_capture`), exactly where the add-on runs them; `smartthings_switch_request` builds the cloud `setInputSource` request (URL+body) for the UI to display (HTTPS firing is out of scope — no TLS crate). Pure builders unit-tested (`sony_bravia_set_input_body`, `format_external_command`, `adb_switch_command_line`, `smartthings_command_url`/`_set_input_body`). Gate: **cargo 34** (4 new builder tests) / `cargo fmt --check` clean / **zero build warnings**. No new crate; `resources/` untouched.
- **Operator verifies (Phase A):** read the new TV section in `lib.rs` + the 4 cargo tests; confirm the wire formats match `tv_control.py` (`_sony_set_hdmi`, `_run_external`), `tv_adb_control.py`, and `tv_smartthings_control._build_command_payload`; confirm `validate_ssh_target`/`validate_ssh_component` guard every host, and that adb/external execute over SSH (not a local Windows subprocess).
- **Operator verifies (Phase C — built app + real TV):** with a real Sony Bravia (PSK), Android-TV (adb), or LG/Samsung/custom TV, invoke the matching `tv_switch_*` command and confirm the TV changes input; for SmartThings, confirm the built request matches what the add-on would POST. **None of this is hardware-validated.**

### Configurator — AVR input-switch commands (Phase 3.1) (PR #177, issue #176)

- **Merged to `main`** (operator chose "merge to main as I go"). Branch `claude/cfg-avr-switch-3a1f0e2b`, base `main`. Implementing SHA: `2bf0663`. Tracks **#176**.
- **What changed (software-verified only):** four per-backend AVR input-switch paths in `lib.rs`, mirroring `resources/lib/avr/`. Pure builders — `denon_input_command` (`SI<INPUT>`), `eiscp_input_payload`/`eiscp_frame` (`!1SLI<hh>` ISCP-framed), `yamaha_input_path` (`/YamahaExtendedControl/v1/main/setInput?input=`), `sony_audio_set_input_payload` (compact key-sorted `setPlayContent`) — plus fire `#[tauri::command]`s `avr_switch_denon` (:23), `avr_switch_eiscp` (:60128), `avr_switch_yamaha` (:80), `avr_switch_sony_audio` (HTTP POST) that open one short-lived socket like `tv_switch_roku`. Gate: **cargo 30** (10 new builder tests) / `cargo fmt --check` clean / **zero build warnings**. No new crate; `resources/` untouched (addon suite unaffected).
- **Operator verifies (Phase A):** read the new AVR section in `lib.rs` + the 10 cargo tests; confirm the wire formats match the add-on drivers (`avr_denon_marantz.py` `SI`, `avr_onkyo_eiscp.py` ISCP frame + `!1SLI`, `avr_yamaha.py` `setInput`, `avr_sony_audio.py` `setPlayContent`), and that `validate_ssh_component` guards each host.
- **Operator verifies (Phase C — built app + real receiver):** with a real Denon/Marantz, Onkyo/Integra/Pioneer, Yamaha, or Sony AVR on the LAN, invoke the matching `avr_switch_*` command and confirm the receiver actually changes input. **None of this is hardware-validated.**

### Configurator — NAS-path capture so the http_handoff default is functional (PR #174, issue #173)

- **Draft PR #174** (branch `claude/cfg-nas-path-capture-7c4e9a02`, base `main`); built on the merged guided-install initiative (#170/#171/#172). Tracks **#173** (D-4 / Phase 1b). Implementing SHAs: `dee2e62` (kodi_now_playing), `dc6f60d` (oppo_http_play), `0f62fe2` (deriveRewrite), `8882605` (capture UI + oppo_playback_info).
- **What changed (software-verified only):** the `http_handoff_svm3` default needs the OPPO-visible media path (`oppo_http_path_from/to`) or it is written-but-inert; this adds the UI + plumbing to *learn* it. New Rust commands `kodi_now_playing` (Kodi JSON-RPC over the existing SSH channel — `Player.GetActivePlayers` then `Player.GetItem{file}`, `kodi.log` fallback), `oppo_playback_info` (best-effort `/getmovieplayinfo` read), and `oppo_http_play` (activate UDP broadcast then `/signin` then `/playnormalfile?payload=`, raw HTTP/1.0 over TCP:436, **no new crate** — pulled forward from Phase 4 PR-4.1). New pure TS `nas_path.ts` (`deriveRewrite` longest-shared-tail prefix rewrite; `parseOppoPlayingPath` best-effort). A capture card on the Player step (`step2.tsx`): observe-both-ends (Capture-from-Kodi / Read-from-OPPO) + a `deriveRewrite` preview + a manual **SMB/NFS** prefix fallback (WebDAV/FTP out of scope — the OPPO can't necessarily mount them). Gate: **cargo 18** / **190 vitest** / `tsc --noEmit` / `vite build`. **No add-on change** (`resources/` untouched → addon suite stays 1045/3).
- **Operator verifies (Phase A):** read `lib.rs` (`kodi_now_playing` / `oppo_playback_info` / `oppo_http_play` + their request/parse builders and the 9 new cargo tests), `nas_path.ts` (`deriveRewrite` / `parseOppoPlayingPath` + the 10 vitest), and the `step2.tsx` `OppoNasPathCard`. Confirm no new crate dep (`Cargo.toml` unchanged), that `validate_ssh_component` guards the OPPO host commands, and that the rewrite contract matches `oppo_control._translate_media_path` (`oppo_http_path_from/to`).
- **Operator verifies (Phase C — built app + real Kodi + OPPO):** on the Player step, play a test file in Kodi → **Capture from Kodi** confirms the Kodi-visible path is read over SSH; play the same file on the OPPO → **Read from OPPO** (or type the OPPO-visible path) and confirm the derived `from → to` is right; **Use this mapping**, finish the wizard, and confirm an `http_handoff_svm3` launch **actually plays on the OPPO** (the previously-inert default). Separately confirm `oppo_http_play` fires a play and whether `/getmovieplayinfo` carries the path (decides auto-read vs. manual). **None of this is hardware-validated.**

### Configurator — wire-level OPPO transcript in the developer debug panel (PR #142 PR-3)

- **Merged to `main`:** PR #153 → merge `832b76e` (branch since deleted). PR-only theme; completes the deferred PR-3 of the developer debug view (PR #142).
- **What changed (software-verified only):** the Rust `oppo_query` command now emits `debug-wire` Tauri events for the raw bytes it sends (the CR-terminated command) and receives (the reply) over TCP:23 — payload carries direction / host / port / hex / lossy-text / length. A new `src/debug/wireListener.ts` subscribes via `@tauri-apps/api/event` and records them through a new `recordWire()` into the existing ring buffer (`log.ts`; `DebugEntry` is now an `ipc` | `wire` discriminated union); `DebugPanel.tsx` renders wire rows (→ sent / ← recv, byte count, hex + text on expand). **Scoped to the OPPO IP-control path only** — `deploy_ssh` / `read_ssh_file` / `deploy_to_userdata` are deliberately NOT instrumented, because their payloads are the generated `settings.xml` (Sony PSK / SmartThings token) and the key-based redactor cannot sanitize a raw byte stream. Off by default (the panel is gated behind Ctrl+Shift+D). Gate: frontend `tsc -b` + **157 vitest** + `vite build`; Rust `cargo check` + `cargo test` (3 `to_hex` tests). No add-on change.
- **Operator verifies (Phase A):** read the `oppo_query` diff (emits sent/recv; the returned reply string is unchanged), `wireListener.ts`, the `log.ts` `ipc`|`wire` union + `recordWire`, and the `DebugPanel` wire-row branch. Confirm only `oppo_query` emits (no ssh/deploy/file command does) and that `statusOf` no longer counts wire frames as errors.
- **Operator verifies (Phase C — built app + real OPPO):** `npm run tauri` (or `cargo`) build the app, launch it, press **Ctrl+Shift+D**, run the Step 2 player test / SVM3 probe against a real OPPO, and confirm the panel shows the sent `#QVM`/`#QPW` bytes and the received `@…` reply (hex + text), filtered to the current step. Confirm **no secrets** appear and that a Tier-A SSH deploy does **not** dump `settings.xml` bytes. **Not hardware-validated.**

### Configurator — Live Session Dashboard: gated live verbose stream (Theme 2 / PR D3)

- **Merged to `main`:** PR #160 → merge `e8d35bf` (code `c69b904`; branch since deleted). Third of three dashboard PRs (D1 #158 → D2 #164 → D3 #160).
- **What changed (software-verified only):** adds a **Live stream** card that opens the configurator's *own* verbose-mode-3 connection to the player and shows the raw `@UPL` / `@UTC` / status push frames live. New Rust (`configurator/src-tauri/src/lib.rs`): a managed `LiveMonitor` + two commands `start_oppo_live_monitor` / `stop_oppo_live_monitor`. Start connects, remembers the prior verbose mode (`#QVM`), switches to `#SVM 3`, and spawns a background `std::thread` that streams each CR/LF-terminated frame to the webview as an **`oppo-live`** event (its own event channel — does **not** depend on the open wire-transcripts draft #153). Stop signals the thread, which **restores the prior verbose mode** and closes; unmounting the dashboard also stops it. Mirrors `resources/lib/oppo/playback_monitor_svm3.py`. Uses `std::thread` + `AtomicBool` (no tokio / **no new dependency**). **No add-on change.** Frontend: a pure `canStartLiveStream(status)` gate + the dashboard card (Start/Stop, frame feed, auto-stop). `cargo test` adds 2 unit tests (`classify_frame`, `parse_verbose_mode`); `dashboard_status.test.ts` adds 2 gate tests. Gate: `tsc --noEmit` + **173 vitest** + `cargo check` + `cargo test` (2) + `vite build` green.
- **⚠️ Dual-subscriber gate (the safety crux):** the OPPO treats verbose mode as a **device-global** setting, so two `#SVM` drivers conflict. The stream is **refused** while the add-on reports an active (`session_state == "starting"`) session (`canStartLiveStream`), and the poll **auto-stops** the stream if a session starts while it is open. This *reduces* but cannot *eliminate* a race (the add-on could start in the ~6s poll window), and the non-conflict can only be confirmed on real hardware.
- **Operator verifies (Phase A):** read the `lib.rs` monitor (start/stop, the `#QVM` -> `#SVM 3` handshake, restore-on-stop in `run_live_loop`, the 2 cargo tests), `canStartLiveStream` + its 2 tests, and the dashboard Live-stream card + the in-poll auto-stop. Confirm there is no new crate dependency (`Cargo.toml` unchanged) and the event name is `oppo-live` (independent of #153's `debug-wire`).
- **Operator verifies (Phase C — on a real OPPO, no add-on session active):** open **Live dashboard** -> **Start**, play a disc/file on the OPPO directly, and confirm `@UPL PLAY` + advancing `@UTC` frames stream in; **Stop** and confirm the player's previous verbose mode is restored (`#QVM`). Then confirm the **gate**: while the add-on is mid-session the Start button is disabled with the paused message, and starting the add-on while streaming auto-stops the stream. **The dual-subscriber non-conflict is NOT hardware-validated** — verify the configurator stream never disrupts an add-on playback session before relying on it.

### Configurator — Live Session Dashboard: current-session panel (Theme 2 / PR D2)

- **Merged to `main`:** PR **#164** → merge `e4118c0` (code `13849f0`; branch since deleted). Second of three dashboard PRs. (Originally PR #159 — GitHub auto-closed it when D1's stacked base branch was deleted on merge and a closed-base PR can't be reopened; the identical D2 code was re-merged via #164.)
- **What changed (software-verified only):** the dashboard gains a **Current session** card that reads the add-on's `oppo203iso-status.json` and shows the session state (in progress / ended / failed), the media file, the preset / routing / monitor, and the `confirmed_playback` / `confirmed_progress` flags (plus OPPO state / UTC ticks / stop reason once stopped). New pure `oppo_status.ts` — the `OppoSessionStatus` type + a tolerant `parseOppoStatus()` mirroring `playback_session.py` `_status` (8 base keys + 3 snapshot keys) and `ADDON_DATA_STATUS_REL` (the sibling of `ADDON_DATA_SETTINGS_REL`). New `dashboard_status.ts` — a pure `statusReadPlan(state)` (tier A -> `read_ssh_file`, tier B -> `read_userdata_file`, manual -> unsupported) and a thin `readOppoStatus()` executor that **reuses the same file-read commands as applyToKodi**. **No Rust change, no new dependency, no add-on change.** The panel is honest that the file is written only at session start/end (a summary, not a live feed). New `oppo_status.test.ts` (5) + `dashboard_status.test.ts` (3). Gate: `tsc --noEmit` + **171 vitest** + `vite build` green.
- **Operator verifies (Phase A):** read `oppo_status.ts` + `parseOppoStatus` tests (confirm a "starting" record parses with null snapshot fields, and wrong-typed/garbage input returns null), `dashboard_status.ts` + `statusReadPlan` tests (tier A/B routing, manual unsupported), and the `SessionCard` in `screens/dashboard.tsx`. Confirm it only **reads** and that tier C shows the manual-mode note rather than erroring.
- **Operator verifies (Phase C — built app + real box):** with a tier A/B deployment, play a file through the add-on, then open **Live dashboard** and confirm the Current-session card matches the box's `oppo203iso-status.json` (state, preset/routing/monitor, confirmed flags). In manual mode confirm the card explains there is no remote link. **Not hardware-validated.**

### Configurator — Live Session Dashboard: device liveness (Theme 2 / PR D1)

- **Merged to `main`:** PR #158 → merge `5755184` (code `7a5ebce`; branch since deleted). PR-only theme (no tracked issue); first of three stacked dashboard PRs (D1 #158 → D2 #164 → D3 #160).
- **What changed (software-verified only):** adds a new terminal **`dashboard`** screen reachable from the final "Setup verified" screen (a new **Live dashboard** button on `screens/test.tsx` `TestSuccess`). It polls device liveness every 6s, reusing the existing one-shot Tauri commands — `tcp_probe` for the Kodi box (SSH :22, or SMB :445 for tier B) and the AV receiver (AVR chain only; control port by backend: Denon/Marantz 23, Yamaha 80, Onkyo/Pioneer 60128), and `oppo_query #QPW` + `parseOppoPowerReply` for the player (reachability + power state). A new pure helper `dashboard_targets.ts` (`livenessTargets(state)`) derives which devices to probe from saved state; the **TV is intentionally omitted** (the wizard never persists a TV IP). Routing wired in `steps.ts` (`ScreenId` / `SCREEN_TO_STEP` / `SCREEN_TO_CHAIN`, mapped to the Test step) + `App.tsx`. **No Rust change, no new dependency, no add-on change, no new emitted settings** — read-only liveness. New `dashboard_targets.test.ts` (5 tests). Gate: `tsc --noEmit` + **163 vitest** + `vite build` green.
- **Operator verifies (Phase A):** read `dashboard_targets.ts` + its 5 tests, `screens/dashboard.tsx`, and the `steps.ts` / `App.tsx` / `test.tsx` wiring; confirm it is additive (the wizard flow + emitted settings are untouched) and the dashboard is reachable only from `test_success` and returns there.
- **Operator verifies (Phase C — built app + real devices):** launch the configurator, finish setup, open **Live dashboard**, and confirm each device's dot reflects reality — Kodi box reachable, the OPPO showing power on/off, and (AVR chain) the receiver reachable; power a device off and confirm the dot flips within ~6s. Liveness depends on the real devices answering. **Not hardware-validated.**

### Add-on + configurator — http_handoff routing: six-option playback (PRs #154/#155/#156/#157)

- **Merged to `main`:** PR #154 `b630b85` (addon presets, reader-only) · #155 `87fbfc6` (addon launch branch) · #156 `4b4d950` (configurator routing pill) · #157 `37e50e9` (configurator JSON payload mode). PR-only theme; extends the four-option architecture to **six** by adding `http_handoff` as a third routing value.
- **What changed (software-verified only):** the routing axis gains `http_handoff` (`settings_reader.PLAYBACK_ROUTING_MODES` / `_PRESET_BY_AXES` / `_ROUTING_ALIASES` + the `playback_architecture` enum), so the four presets become six (`+ http_handoff_legacy` / `http_handoff_svm3`). `run_playback_session` branches the launch on the resolved routing: `http_handoff` runs the new `external_player.fast_start_http` (TV switch + AVR pre-sequence + the community OPPO HTTP file launch, reusing `oppo_control.activate_http_api`/`signin_http_api`/`play_media_http_api`); the other two routings call `fast_start` **unchanged**. The monitor axis (legacy/svm3) is untouched, so confirmation falls out of it (HTTP launch + legacy hold, or + SVM3 confirm). HTTP-launch failure is **non-fatal** (logged; the session still cleans up). The configurator adds an **HTTP Handoff (community NAS)** routing pill on the Kodi-box step, emits the `http_handoff_*` preset triple + `oppo_http_payload_mode=json_payload`, and shows the routing in the final-test readout. **Reuses the existing HTTP functions — no refactor; no new `settings.xml` category** (only existing keys are emitted). Gate: addon pytest **1045/3**, coverage **99%**, ruff + mypy `--strict` **51/0**; configurator `tsc -b` + **158 vitest** + `vite build`.
- **Operator verifies (Phase A):** read the `settings_reader` routing/preset diff (now six presets; default still `playercorefactory_legacy`), `external_player.fast_start_http` + the `run_playback_session` routing branch (confirm the four existing presets still call `fast_start` unchanged), and the configurator `step1`/`mapping` diff (the `http_handoff` pill + the emitted triple).
- **Operator verifies (Phase C — on a real OPPO + NAS):** pick **HTTP Handoff** + a monitor mode in the wizard, deploy, and play a NAS file. Confirm the OPPO launches it via the community HTTP API and the chosen monitor confirms playback (SVM3 `@UPL`/`@UTC`, or the legacy hold), with TV/AVR switching intact. **Limitation / candidate:** the OPPO-visible **path translation** (`oppo_http_path_from` / `oppo_http_path_to`) is **not** auto-emitted — set it for your player's NAS mount namespace (e.g. `/mnt/cifs1`, `/mnt/nfs1`) or the launch sends the raw Kodi path. The community HTTP API + this mapping are **not hardware-validated**; the NFS/SMB mount endpoints (`/login*` / `/mount*`) and `/checkfolderhasBDMV` are deferred (this reuses `/playnormalfile` only).

### Add-on — playback_monitor_mode + four-option preset mapping (Session A / PR A1)

- **Merged:** PR #143 → `main` via `fadd8c9` (code `cbae76e`; branch since deleted). Tracked by ENH #150 (`area:addon`); operator authorized the new reader key in-session (the SVM3 four-option build plan).
- **What changed (software-verified only):** adds the monitor axis `playback_monitor_mode` (`legacy`|`svm3`, default `legacy`) to `settings_reader.DEFAULTS`/`ENUM_VALUES` alongside the existing `playback_architecture` routing axis, plus pure helpers `architecture_preset(routing, monitor)` and `normalize_architecture(settings)` that resolve the four combined presets (`playercorefactory_legacy` / `service_interception_legacy` / `playercorefactory_svm3` / `service_interception_svm3`). The combined `playback_architecture_preset` is configurator-written and is the source of truth **when present**; when absent it is derived from the legacy fields — it has **no** `DEFAULTS` entry on purpose, so it cannot mask a pre-existing `service_interception` install. Mirrors the reader-only `playback_architecture` pattern: **no `settings.xml` UI entry, no `strings.po` change, no runtime playback change** (the value is only read in this PR). New `tests/test_architecture_presets.py` (18 tests) pins the mapping, migration back-fill, drift resolution (preset wins), and the preset↔normalized round-trip guard. Gate green: pytest **994 passed / 3 skipped**, coverage **99%**, ruff check + format clean, mypy `--strict` **49/0**.
- **Operator verifies (Phase A):** read the `resources/lib/kodi/settings_reader.py` diff + the 18 new tests; confirm existing installs map to a `*_legacy` preset (external_player → playercorefactory_legacy, service_interception → service_interception_legacy) and that nothing acts on the value at runtime yet.
- **Operator verifies (Phase C — on the box):** none for this PR — no runtime behavior changes. The monitor branch is wired in PR A3 and SVM3 is exercised end-to-end there.

### Add-on — SVM3 playback monitor (Session A / PR A2)

- **Merged:** PR #144 → `main` via `ccf3638` (code `3b63054`; stacked on PR A1; branch since deleted). PR shows *Closed* not *Merged* — a stacked-branch-delete artifact; the code is on `main`. Tracked by ENH #151 (`area:addon`); relates to the verify-played follow-through (#113).
- **What changed (software-verified only):** new `resources/lib/oppo/playback_monitor_svm3.py` — `OppoSvm3PlaybackMonitor`, a persistent verbose-mode-3 (`#SVM 3`) client built on the same line-reading + stop/play vocabulary as `oppo_tcp_client.py`. It queries the current verbose mode (`#QVM`), switches to mode 3, parses `@UPL` playback-status and `@UTC` time-code push lines, and treats playback as confirmed **only** from OPPO events — `@UPL PLAY` → `confirmed_playback`, an *advancing* `@UTC` → `confirmed_progress` — never from a sent command. Bounded ring buffer + summary/state-change logging (per-second `@UTC` is **not** logged in production; `full_event_log` logs every raw line); previous verbose mode is restored on exit, even after the socket drops. Tuning ships as code constants (no new persistent settings). **Not yet wired into the runtime** — PR A3 selects it when `playback_monitor_mode=svm3`. Registered in the mypy `--strict` allowlist (`mypy.ini` + `pyproject.toml`) and the `resources/lib/__init__.py` legacy-name bucket. New `tests/test_svm3_playback_monitor.py` (32 hermetic tests, fake socket + scripted clock) → the module is at **100%** coverage. Gate green: pytest **1026 passed / 3 skipped**, coverage **99%**, ruff clean, mypy `--strict` **50/0**.
- **Operator verifies (Phase A):** read `playback_monitor_svm3.py` + the 32 tests; confirm the `confirmed_playback` / `confirmed_progress` split (command dispatch is never treated as proof), the restore-on-exit, and that nothing imports/uses the monitor at runtime yet.
- **Operator verifies (Phase C — on the box):** deferred to PR A3 / Session B, where SVM3 is selectable. On a real OPPO UDP-203/205: `#QVM` returns the current mode, `#SVM 3` is accepted, `@UPL`/`@UTC` arrive during playback, and the previous verbose mode is restored on exit. Chinoppo clones: confirm `#SVM 3` is accepted or fails honestly. **Not hardware-validated.**

### Add-on — shared run_playback_session engine + four-option rewire (Session A / PR A3)

- **Merged:** PR #145 → `main` via `421c2f0` (code `d5ba5ab`; stacked on PR A2; branch since deleted). PR shows *Closed* not *Merged* — same stacked-branch-delete artifact; the code is on `main`. Tracked by ENH #152 (`area:addon`).
- **What changed (software-verified only):** new `resources/lib/kodi/playback_session.py` — `run_playback_session(settings, media_file, launch_source)`, the single sequence both routings now use: `mark_session_active` → `fast_start` → monitor → `fast_return` → `clear_session_active`. The monitor branch is chosen by `playback_monitor_mode` (via `normalize_architecture`): **legacy** runs the existing `hold_playback` dispatcher unchanged; **svm3** runs `OppoSvm3PlaybackMonitor` and **falls back to the legacy hold if it cannot connect**. A split-truth status JSON (`oppo203iso-status.json`) is written next to the session sentinel (launch_source / preset / routing / monitor_mode / confirmed_playback / confirmed_progress / oppo_playback_state / stop_reason) so confirmation is reported honestly, never as one success flag. `external_player.main()` and `service._run_interception()` now both delegate here (the inline duplicate sequences are gone); `fast_start`/`hold_playback`/`fast_return`/`mark`/`clear` stay public and unchanged. Registered in the mypy `--strict` allowlist + the `resources/lib/__init__.py` bucket. New `tests/test_playback_session_modes.py` (10 tests) → `playback_session.py` at **100%**; the `external_player` `__main__` entrypoint test still passes (`main()` injects its own module). Gate: pytest **1036 passed / 3 skipped**, coverage **99%** (no new gaps — missing-statement count unchanged at 16), ruff clean, mypy `--strict` **51/0**, layout/docs/version/i18n green.
- **Operator verifies (Phase A):** read `playback_session.py`, the `external_player.main()` / `service._run_interception()` diffs (both now call `run_playback_session`), and the 10 tests. Confirm the legacy path is the same call sequence (mark → fast_start → hold → fast_return → clear) and that the SVM3 branch falls back to legacy on connect failure. **Heads-up:** the paused teaching-commentary wip branch on `external_player.py` will need a rebase — this PR changed `main()` logic.
- **Operator verifies (Phase C — on the box):** end-to-end, all four presets. Legacy presets: behavior unchanged (playercorefactory launches the controller; service intercepts; the chosen `hold_mode` ends the hold). SVM3 presets: OPPO confirms playback via `@UPL`/`@UTC`, the previous verbose mode is restored, and `oppo203iso-status.json` shows `confirmed_playback`/`confirmed_progress`. SVM3 with an unreachable control port → falls back to the legacy hold (no hang). **Not hardware-validated.** (`playback_monitor_mode` / preset are seeded by the configurator in Session B; until then, set them manually in the deployed `settings.xml` to exercise SVM3.)

### Configurator — wizard renumber + new Step 3 "Playback mode" scaffold (Session B / PR B1)

- **Merged:** PR #146 → `main` via `4680278` (code `df4012c`; branch since deleted). PR-only theme (no tracked issue); pairs with the addon Session A SVM3 PRs #143–#145.
- **What changed (software-verified only):** inserts a new **Step 3 "Playback mode"** right after Player and renumbers the rest — **TV 3→4, HDMI Input 4→5, AV Receiver 5→6**. Mechanical rename only: `screens/step3|4|5.tsx`→`step4|5|6.tsx`, `Step3|4|5*` components→`Step4|5|6*`, `step3_*|step4_*|step5_*` ScreenIds→`step4_*|step5_*|step6_*`, `step4NextScreen`→`step5NextScreen`, plus `steps.ts` (`StepId`/`ScreenId`/`STEPS`/`SCREEN_TO_STEP`/`SCREEN_TO_CHAIN`/`firstScreenOfStep`) and the `App.tsx` renderer map. Player now routes to the new `step3_mode` (→ TV `step4_brand`); the new screen is a **minimal placeholder** (the legacy-vs-SVM3 choice lands in PR B2). All step-number display copy + comments updated to the new numbering (`"Fix TV → Step 4"`, `owner="Step 4 · TV / Step 5 input capture"`, the AVR `screen-num` badge `6`, "set up the receiver in step 6", and the `mapping.ts`/`steps.ts`/db-guard comments) per AGENTS.md "names match what the user sees." **No TV/HDMI/AVR/Player logic changed.** Gate: `tsc -b` + **146 vitest** + `vite build` green.
- **Operator verifies (Phase A):** read the rename diff — confirm it is purely id/number/component/file renames + the Player→`step3_mode` redirect + the placeholder, with no behavior change to the existing steps; the stepper + per-screen numbers read 0 · Player(2) · Playback mode(3) · TV(4) · HDMI(5) · AVR(6) · ✓.
- **Operator verifies (Phase C — built app):** launch the configurator and walk Player → **Playback mode** (placeholder) → TV → HDMI → AVR → Test; confirm the numbering is consistent everywhere and resume/persistence still lands on valid screens.

### Configurator — Playback-mode choice + emit four-option settings triple (Session B / PR B2)

- **Merged:** PR #147 → `main` via `f06e1de` (code `5d24d5f`; stacked on B1; branch since deleted). PR shows *Closed* not *Merged* — stacked-local-merge artifact; the code is on `main`. PR-only theme; pairs with addon PR #143 (which reads these keys).
- **What changed (software-verified only):** the new Step 3 "Playback mode" screen now offers **SVM3** (recommended for new installs) vs **Legacy** (compatibility), writing `state.monitorMode` (new `MonitorMode` type; default `legacy`). `mapping.ts` emits the consistent **triple** — `playback_architecture` + `playback_monitor_mode` + the derived `playback_architecture_preset` (e.g. `playercorefactory_svm3`) — which the add-on (PR #143) reads, treating the preset as source of truth. SVM3 is labelled "recommended for validation / new installs," **not** hardware-validated. `mapping.test.ts` adds 5 tests pinning the triple consistent across all four combos. Gate: `tsc -b` + **151 vitest** + `vite build` green.
- **Operator verifies (Phase A):** read the Step 3 copy + the `mapping.ts` emit + the 5 new mapping tests; confirm the triple is internally consistent for all four combos and the default is `legacy` / `playercorefactory_legacy`.
- **Operator verifies (Phase C — built app + box):** in the wizard pick SVM3 vs Legacy at Step 3, finish + deploy, and confirm the add-on `settings.xml` carries a consistent `playback_architecture_preset` + `playback_monitor_mode` and the add-on resolves the matching monitor. (SVM3 capability is probed in PR B3.) Not hardware-validated.

### Configurator — SVM3 capability probe in the player test (Session B / PR B3)

- **Merged:** PR #148 → `main` via `caaba1b` (code `27c01d2`; stacked on B2; branch since deleted). PR shows *Closed* not *Merged* — same artifact; the code is on `main`. PR-only theme; pairs with addon PRs #144/#145.
- **What changed (software-verified only):** the Step 2 player test now runs an **SVM3 capability probe** after two-way control confirms — reusing the existing `oppo_query` Tauri command (**no Rust change**): `#QVM` (read current verbose mode) → `#SVM 3` (accepted?) → `#SVM <prev>` (restore, leaving the player's mode untouched). New pure parsers `parseOppoVerboseMode` / `parseSvm3Accepted` (`probes.ts`, +4 vitest). The result is stored as `state.svm3Supported` and **recommends the matching Playback-mode default** (svm3 on success, legacy otherwise); the user can still override at Step 3. A callout reports supported / not-detected, and SVM3 absence **never fails** the power test (legacy works regardless). The Step 3 SVM3 tile shows the per-player result. Gate: `tsc -b` + **155 vitest** + `vite build` green.
- **Operator verifies (Phase A):** read the `probeSvm3` flow + the 4 new probe-parser tests; confirm the probe restores the previous verbose mode, never gates the power-test pass, and that SVM3 stays labelled recommended-for-validation (not validated).
- **Operator verifies (Phase C — on the box):** with a real OPPO, run the player test → `#QVM`/`#SVM 3` succeed → "SVM3 supported" and Step 3 pre-selects SVM3; with a clone that rejects `#SVM 3` → "not detected" and Step 3 defaults to Legacy. Confirm the player's verbose mode is unchanged after the probe. Not hardware-validated.

### Configurator — final-test status readout (four-option + SVM3 honesty) (Session B / PR B4)

- **Merged:** PR #149 → `main` via `f90da27` (code `2dfa86c`; stacked on B3; branch since deleted). PR shows *Closed* not *Merged* — same artifact; the code is on `main`. PR-only theme.
- **What changed (software-verified only):** the final **Playback Test** confirmation screen (`TestConfirm`) now reports the four-option pieces **separately** — a "What this test covers" readout of **Kodi route** (Playercorefactory / Service interception), **Playback confirmation** (SVM3 — the player reports playback / Legacy — timed-polled hold), and **TV / AVR** (backend or none), derived from wizard state. For SVM3 it adds an honest note: the add-on treats playback as confirmed only once the player reports it (writing `oppo203iso-status.json`), so a disc that plays but isn't reported confirmed means the player isn't sending status — not a playback failure. The three self-report questions + step-owner routing are unchanged (owners were corrected to the new numbering in B1). Presentational only — no settings/logic change. Gate: `tsc -b` + **155 vitest** + `vite build` green.
- **Operator verifies (Phase A):** read the `TestConfirm` diff; confirm the readout reflects the chosen routing / monitor / TV-AVR and the SVM3 note is honest (no hardware-validated claim).
- **Operator verifies (Phase C — built app):** run the wizard to the Playback Test under each monitor mode; confirm the readout matches what was configured and the SVM3 note appears only for SVM3.

### Configurator — dedicated Step-5 receiver restore-input field (AVR-chain restore, #138 follow-up)

- **Branch:** `claude/avr-receiver-restore-input-a7f2c419`. PR-only theme (no tracked issue); follow-up to PR #138.
- **What changed (software-verified only):** Step 5 now captures a dedicated **"Kodi input on the receiver"** field (`state.avrKodiInput`), shown only in the AVR chain for native (non-Sony) backends. `mapping.ts` sources `avr_restore_input` from it instead of reusing the TV's `kodiInput` (the Step-4 TV HDMI port). A blank value writes no restore input — the add-on treats that as a non-fatal skip (`resources/lib/avr/avr_sequence.py`). `avr_restore_input` is `type="string"` read as a free-text receiver input, so there is **no add-on change**. The end-of-wizard test summary now shows receiver inputs (not "HDMI N") in the AVR chain. TV chain unchanged (regression-pinned). `tsc --noEmit` + `tsc -b` + `vite build` + **125 vitest** green.
- **Operator verifies (Phase A):** read the `state.ts` / `mapping.ts` / `step5.tsx` / `test.tsx` diff + the updated `mapping.test.ts` cases (restore now sourced from `avrKodiInput`; the dedicated-field pin proves it is NOT `kodiInput`; blank ⇒ power-on but no restore).
- **Operator verifies (Phase C — on hardware):** in an AVR-chain setup, enter a **distinct** receiver input for the Kodi box (e.g. `CBL/SAT`), different from the player input (e.g. `BD`); confirm that on playback exit the receiver returns to the **Kodi** input — not the player input, and not a TV HDMI number. Candidate mapping — confirm against a real receiver. **Migration note:** an existing AVR-chain config that relied on the old numeric reuse should re-open Step 5 and set this field, or restore is skipped (non-fatal).

### Configurator — AVR DB grown with 2026 model-year candidates (15 rows, validated:false)

- **Branch:** `claude/avr-db-2026-models-3e8b9d04`. PR-only theme (no tracked issue); Configurator theme 3 from the resume backlog. Researched candidates for operator fact-check.
- **What changed (software-verified only):** added 15 `validated:false` 2026 model-family rows to **both** copies of `avr-models.json` (kept byte-identical, guarded by #134): Denon AVR-X2900H/X3900H, Marantz AV 30 (pre/pro), Yamaha RX300A/RX500A, Onkyo TX-RZ31/51/61/71, Integra DRX-R1/DRX-7, Arcam AVA15/AVA25/AVA35 + AVP45. Bumped `db_version` → `2026.05.31-avr-2018-2026-region-schema` and `scope.years` → [2018, 2026]; added `2026` to the Step-5 `AVR_YEARS` filter. No new lineups (all rows attach to existing protocol families, so backends resolve unchanged). `tsc --noEmit` + `vitest` (123) + `vite build` green. Sourced from 2026 launch coverage (CES 2026 / ISE 2026 / spring announcements) — citations in the PR body.
- **Operator verifies (Phase A):** fact-check the 15 rows against real product data — model names, model-year (especially Integra DRX vs the 2024 generation), channel counts, regions, and the control backend per model. Two caveats are baked into the rows' `control_notes`: (a) Yamaha RX300A/RX500A are entry tier and may lack MusicCast/YXC network control (predecessor RX-V385 had none) — confirm or downgrade to `custom_command`; (b) Integra year/availability needs confirmation. **No 2026 rows** were added for Pioneer (CES 2026 was in-vehicle), Sony (only "early looks" + soundbars), Anthem, or NAD — no verifiable new AVR found.
- **Operator verifies (Phase C — on the built app / hardware):** in Step 5 pick a 2026 brand, confirm the new `2026` year filter surfaces the rows and the candidate backend + reachability probe behave; validate control against a real 2026 unit where available. All rows are candidate mappings — not hardware-validated.

### Configurator — TV DB grown with 2026 lineups + a two-copy consistency guard (28 rows, validated:false)

- **Branch:** `claude/tv-db-2026-models-7b1f4a92`. PR-only theme (no tracked issue). Researched candidates for operator fact-check.
- **What changed (software-verified only):** the TV DB already covered 2025 (44 rows); this adds **28 `validated:false` 2026 model-family rows** to **both** copies of `tv-models.json` — now kept byte-identical by a NEW `configurator/src/tv_db_consistency.test.ts` (mirrors the AVR `#134` guard the TV DB never had). Rows: Samsung 7 (S95H/S90H/S85H, QN80H/QN70H, Micro RGB, The Frame), LG 6 (G6/C6/B6/W6, QNED evo, Micro RGB evo), Sony 2 (BRAVIA 9 II / 7 II True RGB Mini-LED), TCL 7 (X11L/QM8L/QM7L/QM6L/RM9L/C8L/C7L), Hisense 6 (U6SF/U6SF Pro/U7SG/U7SF/UR9/UR8). All attach to existing lineups (no new lineups). `scope.years` → [2018, 2026]; `2026` added to the Step-3 year filter. `tsc --noEmit` + `vitest` (131) + `vite build` green. Sourced from CES 2026 / spring-2026 coverage — citations in the PR body.
- **Operator verifies (Phase A):** fact-check the 28 rows against real product data — names, model-year, platform → control backend, regions. Caveats are recorded in each row's `notes`/`mapping_confidence`: **Hisense** platform varies by region (U7SG/U7SF assumed Google TV → `adb`, UR9/UR8 assumed VIDAA → `custom_command`, U6SF/Pro Fire TV → `custom_command`) at `low`/`medium` confidence — confirm before relying on the backend; **Samsung QN90** 4K has no 2026 successor (so no QN90H); **Sony** carried-over 2025 sets (BRAVIA 2 II/3 II/5/8 II) stay under their existing 2025 rows. `db_version` stays `2026.05.31` (today; the strict `YYYY.MM.DD` format has no sub-day field to bump).
- **Operator verifies (Phase C — built app / hardware):** in Step 3 pick a 2026 brand, confirm the new `2026` year filter surfaces the rows and the resolved platform/backend is right; validate control against a real 2026 set where available. All rows are candidate mappings — not hardware-validated.

### Configurator — developer debug view (per-step IPC command log)

- **Branch:** `claude/configurator-debug-view-5a2e8c10`. PR-only theme (no tracked issue).
- **What changed (software-verified only):** a developer-only debug panel. New `src/debug/log.ts` (a redacting 500-entry ring buffer + current-step tag), new `src/ipc.ts` (an `invoke` wrapper recording every call as a pure pass-through), all wizard `invoke` sites migrated to it, and a global docked `src/shell/DebugPanel.tsx` mounted once in `App.tsx` that shows the captured commands (sent args, result/error, timing) filtered to the current step. **Gated behind dev mode — off by default, toggled with Ctrl+Shift+D** (persisted in localStorage), so ordinary users never see it. Secrets are redacted (psk/token/password/secret/credential keys blanked; long blobs truncated). `tsc --noEmit` + `vitest` (136) + `vite build` green. No add-on change.
- **Operator verifies (Phase A):** read the diff — confirm `redact()` covers the secret keys you care about (esp. `sony_avr_psk`/`avrSonyPsk` and the deploy file blobs), the wrapper is a pure pass-through (same args/result/error), and that **only `ipc.ts`** imports `invoke` from `@tauri-apps/api/core`.
- **Operator verifies (Phase C — built app):** launch the configurator, press **Ctrl+Shift+D**, then walk a hardware-touching step (Step 2 OPPO query, Step 3 TV probe, Step 5 receiver probe, Step 1 SSH/SMB) and confirm the dock shows each command with sent args + raw reply/error + timing, filters to the current step (toggle to all), and that **no PSK/token is visible**. Confirm the panel is absent until the hotkey is pressed. (Wire-level raw-byte transcripts from Rust were scoped as an optional later PR and are not in this change.)

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
- **Re-confirmed on `main`@`3c0e1c8` (2026-06-02):** still green on current `main` — TV DB is now
  **324 models** across all five brands (samsung 89 / lg 65 / tcl 64 / hisense 57 / sony 49),
  `schema_version: 2`; `vitest` `tv_db_consistency` 8 + `tvdb` 16 pass; `step4.tsx:96,154,206`
  region-first filter + v2 fields confirmed in code. Every issue scope bullet is satisfied — **ready to close.**

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
- **Re-confirmed on `main`@`3c0e1c8` (2026-06-02):** still green on current `main` — `players.test.ts`
  10 + `tests/test_players_db_consistency.py` **7/7** (pins the two copies identical, `enum_order` ↔
  `settings_reader` ↔ `settings.xml`, full taxonomy/profile/alias coverage); `step2.tsx:70` surfaces
  markets/wake/class/NAS. Every issue scope bullet is satisfied — **ready to close.**

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
