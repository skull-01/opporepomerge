# Xnoppo V3 Adoption and Decision-Tree Enhancements

**Initiative:** Pure-HTTP/436 OPPO control — PRs 1–6 (cross-area: 🟦 add-on · 🟩 configurator)
**Status:** ✅ **SHIPPED 2026-06-02** — all 6 PRs merged to `main`; released as add-on **v2.9.15** + configurator **v0.8.0** (configurator holds the repo "Latest"). PR1 #208 · PR2 #210 · PR3 #212 · PR6 #214 · PR4 #216 · PR5 #218; ENH #207/#209/#211/#213/#215/#217 (open for operator close). Phase-C hardware validation is the only remaining work.
**Grounded against:** `main`@`c200349` (2026-06-02)
**Companion artifacts:** `docs/BUILD_PLAN.md` (Active-initiative summary), `build/configurator_decision_tree.html` (decision tree), `Xnoppo_Elite_V3_OPPO_HTTP_Flows_Functions_Commands.md` (protocol reference)
**Provenance:** adopts the Xnoppo Elite V3 / `emby-chinoppo-bridge` (MIT) pure-HTTP/436 control model.

> This is the detailed, code-grounded build-of-record for the initiative. Every `file:line`
> anchor below was confirmed against the live tree on 2026-06-02. It expands the one-paragraph
> "Active initiative" block in `docs/BUILD_PLAN.md` into the canonical Plan format
> (theme → per-PR scope → dependency chain → rollup → risks → verification → session split).

---

## Grounding findings (refinements vs the original doc)

1. **The preset matrix is now a 3-place contract, not 2.** Since PR #203 the single source of
   truth is split across **(a)** the add-on Python registries in
   `resources/lib/kodi/settings_reader.py:217–245`, **(b)** the shared
   `configurator/src/presets-db/playback-presets.json` (`schema_version:1`, 6 presets), and
   **(c)** the configurator `presetsdb.ts` / `mapping.ts`. It is pinned by **two** guards:
   `tests/test_playback_presets_consistency.py` (Python↔JSON) and `mapping.test.ts` (TS↔JSON).
   PR2's 6→7 flip must land in **all three places + both guards in one PR**.

2. **The 7th preset is an *asymmetric* cell.** `monitor_modes` gains `"http"` (→3) but
   `preset_by_axes` gains only **one** row (`http_handoff×http`) → **7 presets, not 9**. The
   JSON's `preset_by_axes` is an explicit list so it models asymmetry naturally — but any guard
   computing a full `routing×monitor` cross-product would wrongly expect 9. Verify
   `test_playback_presets_consistency.py` asserts the explicit list, not a Cartesian count.

3. **A clamp is mandatory in PR2.** `architecture_preset`
   (`settings_reader.py:256–260`) ends in a bare `_PRESET_BY_AXES[(routing, monitor)]`. Today the
   `if monitor not in PLAYBACK_MONITOR_MODES` guard catches junk; once `"http"` joins
   `PLAYBACK_MONITOR_MODES` (`:218`), `(playercorefactory,"http")` passes the guard then
   **KeyErrors**. PR2 must add `if (routing, monitor) not in _PRESET_BY_AXES: monitor = "legacy"`
   in both `architecture_preset` (`:256`) and `normalize_architecture` (`:273–283`).

4. **Cross-screen axis coupling.** Routing (`playbackArchitecture`) is chosen on **Step 1 (Kodi
   box)** (`mapping.ts:213` comment); the monitor axis (`monitorMode`) on **Step 4 · Playback
   mode** — file `configurator/src/screens/step3.tsx`, screen id `step3_mode`, displayed "Step 4"
   per the documented id↔number divergence in `steps.ts:77`. The "Pure HTTP" pill must set **both**
   axes (`monitorMode:"http"` + `playbackArchitecture:"http_handoff"`) so `mapping.ts:220`'s
   `` `${routing}_${monitorMode}` `` emits a valid `http_handoff_http`; the add-on clamp backstops
   any inconsistent stored state.

5. **All 7 new settings are genuinely absent** from `resources/settings.xml` (verified). Per
   `AGENTS.md`, new persistent keys need operator sign-off — recorded in "Build decisions" below.

6. **PR1 is purely additive.** Existing HTTP fns (`oppo_control.py`: `_http_get:330`,
   `activate_http_api:346`, `signin_http_api:357`, `_disc_folder_root:377`, `_build_json_payload:396`)
   are untouched; PR1 adds new siblings reusing `_http_get`. `tests/test_oppo_http_pure.py` does
   **not** exist yet (correctly new). Capability gate already exists:
   `resources/lib/oppo/hardware_presets.py:218 supports_http()` + per-model `http_api_436` flags
   (`settings_reader.py:619+`).

---

## Theme

**Pure-HTTP/436 OPPO control** — *"one 7th preset (`http_handoff_http`) that launches + monitors +
commands + mounts entirely over HTTP/436, as the new default, without disturbing the existing six."*

- **In scope:** a 7th preset + `http` monitor axis; pure-HTTP orchestration (mount→play→confirm);
  TCP/HTTP-selectable post-install process monitor; `checkfolderhasBDMV`-first-with-fallback disc
  navigation on **both** HTTP and TCP launch paths; selectable confirm-gated HDMI switching
  (`play_delay_hdmi`/`av_delay_hdmi`, ISO/BDMV ≥6 s); Refresh-Rate (5 s) and Auto-Healing
  (ISO resend-once) options.
- **Frozen & guarded:** the **6 existing presets + their TV/AVR sequencing stay byte-identical**
  unless a new (default-off) option is opted into — pinned by `tests/test_architecture_presets.py`
  (`==6`→`==7`), `tests/test_playback_session_modes.py` (per-routing dispatch),
  `tests/test_playback_presets_consistency.py` (3-way matrix), `mapping.test.ts` (emits-all),
  `tests/test_v2910_build18`. **OPPO TCP command map untouched.**

---

## Per-PR scope

### PR 1 — HTTP primitives (🟦 add-on, function-only / unwired) · ~300 LOC · **Low**
- `resources/lib/oppo/oppo_control.py` (after `_http_get:330`): add `send_remote_key_http`,
  `get_global_info` + `global_info_is_playing`, `get_playing_time`, `login_smb`/`login_nfs` +
  share-list getters, `mount_smb`/`mount_nfs` (`lstrip("/")`, no unmount-first),
  `check_folder_has_bdmv`, `detect_nfs` — all reusing `_http_get`; every failure raises `OppoError`.
- No change to the matrix, dispatch, `fast_start*`, or `settings.xml`. Nothing calls these yet.
- **Tests:** new `tests/test_oppo_http_pure.py` — mock `urllib.request.urlopen`; assert each
  primitive's URL/verb + that every non-200 / URLError raises.

### PR 2 — 7th preset + `http` monitor (🟦🟩 CROSS-AREA, one PR) · ~240 LOC · **High**
- 🟦 `settings_reader.py:218` `PLAYBACK_MONITOR_MODES += ("http",)`; `:219` add
  `"http_handoff_http"` →7; `:237` `_PRESET_BY_AXES[("http_handoff","http")] = "http_handoff_http"`;
  **clamp** invalid `(routing,"http")` at `:256` and `:273–283`.
- 🟦 new `OppoHttpPlaybackMonitor` (polls `getglobalinfo`/`getplayingtime` every
  `oppo_http_refresh_seconds`, fallback-safe → returns `None` like svm3) + an `http` branch in
  `_dispatch_monitor` (`playback_session.py:151–158`).
- 🟩 `state.ts:47` `MonitorMode |= "http"`; combined **"Pure HTTP"** pill in `screens/step3.tsx`
  (sets `monitorMode:"http"` **and** `playbackArchitecture:"http_handoff"`);
  `presets-db/playback-presets.json` →7 (add `"http"` to `monitor_modes`, one `preset_by_axes`
  row); `presetsdb.ts` follows.
- **Tests:** `test_architecture_presets.py` `==6`→`==7` + clamp cases;
  `test_playback_session_modes.py` http-dispatch case; `test_playback_presets_consistency.py` +
  `mapping.test.ts` updated to the 7-entry asymmetric matrix + an "emits `http_handoff_http`"
  assertion; new `test_playback_monitor_http.py`.

### PR 3 — pure-HTTP orchestration: mount + HTTP command + ISO auto-heal + HTTP-path BDMV (🟦) · ~260 LOC · **High (HW)**
- Wire into `external_player._start_oppo_http:163` / `fast_start_http:196`: wake
  (`send_remote_key_http PON` + UDP activate) → signin → `getdevicelist` / `detect_nfs` → login →
  share-list → mount → **disc-aware play** (ISO: `STP` then resend after
  `oppo_http_iso_autoheal_after_seconds` when `oppo_http_iso_autoheal`; **BDMV:
  `check_folder_has_bdmv` → fallback `playnormalfile`**; normal: `playnormalfile`) → confirm via
  `getglobalinfo`. Capability-gated (`supports_http`) + every step fallback-safe (failures stay
  non-fatal, as `_start_oppo_http` is today).
- New settings: `oppo_http_iso_autoheal` (bool, true), `oppo_http_iso_autoheal_after_seconds`
  (int, 20).
- **Tests:** `test_oppo_http_orchestration.py` — mocked end-to-end sequence; ISO auto-heal fires
  once; BDMV-check→fallback; non-fatal on each failure.

### PR 4 — default flip (all installs) + process-monitor TCP/HTTP + docs (🟦🟩) · ~160 LOC · **High**
- 🟩 `state.ts:145` default → `http_handoff` + `monitorMode:"http"` (Step 4 default = Pure HTTP);
  the post-install process monitor honors **TCP (QPL/#SVM3) OR HTTP (`getglobalinfo`)** per the
  Step-4 choice; refresh-rate UI (`oppo_http_refresh_seconds`, int, 5).
- 🟦 `normalize_architecture` keeps legacy derivation when no preset is stored (existing installs
  unchanged — verified the back-fill at `:273–283`).
- Docs: `BUILD_PLAN.md` D-A default → `http_handoff_http`; `AGENTS.md` norm; checklist;
  `build/configurator_decision_tree.html`.
- **Tests:** `mapping.test.ts` default-emits-`http_handoff_http`; dashboard process-monitor
  transport-select test; an existing-install-unchanged regression (Python + JSON).

### PR 5 — selectable confirm-gated HDMI switching (🟦🟩 cross-cutting, gated) · ~180 LOC · **High**
- 🟦 new `resources/lib/.../hdmi_sequencing.py` — `compute_play_delay` (ISO/BDMV →
  `max(play_delay_hdmi, 6)`) + an ordering helper, gated into the shared TV-switch path
  (`external_player._safe_tv_switch` / `fast_start`); confirm source = active monitor;
  **legacy = timed delay** (#113 caveat). **Default `immediate` = today's frozen behavior.**
- 🟩 `hdmi_switch_mode` (enum, `immediate`), `play_delay_hdmi` (int, 2), `av_delay_hdmi` (int, 0)
  + Step-5/6 UI.
- **Tests:** `test_hdmi_sequencing.py` pins `immediate` == current path; ISO/BDMV ≥6 s; configurator
  UI emits the three keys.

### PR 6 — TCP-path BDMV adoption (🟦🟩 frozen-routing, gated) · ~140 LOC · **High**
- 🟦 extract PR3's disc-aware play helper; wire `check_folder_has_bdmv`-first-fallback into the
  **TCP** launch path (`external_player.fast_start:148` → `start_oppo_after_optional_delay`). New
  `oppo_bdmv_checkfolder` (bool, **on**), capability-gated + **fallback-safe to today's
  `_disc_folder_root:377`**.
- 🟩 BDMV toggle UI.
- **Tests:** `test_tcp_bdmv.py` pins **off path == current frozen `_disc_folder_root` behavior**;
  on-path probes BDMV then falls back.

---

## Dependency chain

```
PR1 ─┬─> PR2 ───────────────> PR4
     ├─> PR3 ──> PR6 ────────> PR4
     └──────────────────────── PR5 (independent)
```

## 📊 Plan rollup

| PR | Area | ~LOC | Risk |
|----|------|------|------|
| 1 | 🟦 | ~300 | **Low** — additive, unwired, fully unit-mockable |
| 2 | 🟦🟩 | ~240 | **High** — 3-place matrix flip + clamp; a slip silently breaks one of the other 6 presets |
| 3 | 🟦 | ~260 | **High (HW)** — undocumented HTTP mount/play; mitigated by fallback-safe + capability gate |
| 4 | 🟦🟩 | ~160 | **High** — default-for-all flip; existing installs must stay on derived legacy |
| 5 | 🟦🟩 | ~180 | **High** — touches frozen TV/AVR sequencing; gated default-off (`immediate`) |
| 6 | 🟦🟩 | ~140 | **High** — touches frozen TCP routing; gated fallback-safe, off-path pinned |

## New settings (all 🟩 configurator-owned; operator sign-off recorded below)

| Setting | Type | Default | Drives | PR |
|---|---|---|---|---|
| `playback_architecture_preset` (extended) | enum | derived | adds `http_handoff_http` (7th) | 2 |
| `oppo_http_refresh_seconds` | int | 5 | monitor + process-monitor poll ("Refresh Rate") | 2 / 4 |
| `oppo_http_iso_autoheal` | bool | true | ISO resend-once ("Auto-Healing") | 3 |
| `oppo_http_iso_autoheal_after_seconds` | int | 20 | auto-heal threshold | 3 |
| `oppo_bdmv_checkfolder` | bool | true | checkfolderhasBDMV-first (both paths) | 6 |
| `hdmi_switch_mode` | enum | immediate | selectable confirm-gated HDMI switching | 5 |
| `play_delay_hdmi` | int | 2 | pre-TV render delay (ISO/BDMV ≥6) | 5 |
| `av_delay_hdmi` | int | 0 | TV→AVR stagger | 5 |

## ⚠️ Risk callouts

- **Frozen-behavior guards (merge-blockers).** The 6 existing presets + TV/AVR sequencing + OPPO
  TCP command map stay byte-identical. Pinned by `test_architecture_presets.py`,
  `test_playback_session_modes.py`, `test_playback_presets_consistency.py`, `mapping.test.ts`,
  `test_v2910_build18`. PR5/PR6 each pin the **unchanged path** explicitly (`immediate`,
  `oppo_bdmv_checkfolder=off`).
- **Undocumented-API-as-default.** HTTP/436 mount/monitor/command/BDMV is community-reverse-
  engineered + firmware-dependent. Every HTTP step in PR3/PR6 is **fallback-safe + capability-gated**
  (`supports_http`) so a stock/older OPPO degrades, never bricks — the gate for any default flip.
- **Live-verify caveat (honest signature).** Verifiable in-session: `tsc` / `vitest` / `vite build`,
  `pytest` / `ruff` / `mypy` / coverage, mocked-`urlopen` unit tests, and browser-rendering the new
  pill/toggles on the vite dev server. **Not** verifiable in-session: real HTTP/436 mount, play,
  `getglobalinfo` confirm, ISO auto-heal, BDMV probe, HDMI timing on real hardware. **PR3/PR5/PR6
  real behavior is Phase-C, not hardware-validated.**
- **#113 caveat.** The `legacy` monitor has no start-confirmation, so PR5's `after_playback_confirm`
  degrades to a timed delay there (carried forward, not regressed).
- **Overlap.** None in flight (0 open PRs). PR2 is the one true cross-area contract change — build
  add-on + JSON + configurator + both guards in the **same** PR.

## Verification regime (per PR)

- **Add-on:** `cd D:\Git\script.oppo203.iso.external; .venv\Scripts\python.exe -m pytest -n auto --basetemp=build\_pt`
  + `ruff check .` + `ruff format --check .` + mypy `--strict` gate + the **serial 99% coverage
  gate** (never `-n auto`).
- **Configurator:** `cd D:\Git\script.oppo203.iso.external\configurator; npx tsc --noEmit; npm run build`
  + `vitest`.
- Then: draft PR (software-only signature), SHA-comment on the filed ENH, a Phase A/C row in
  `docs/MANUAL_VERIFICATION_CHECKLIST.md`, **only the operator closes**.

## Session split (one theme; ≤4 PRs/session soft cap — overridden for this autonomous run)

- **Session A — PR1 + PR2** (software-complete; the matrix flip + primitives).
- **Session B — PR3 + PR6 + PR4** (orchestration + BDMV + default flip; HW-gated).
- **Session C — PR5** (independent HDMI sequencing).

---

## Build decisions (front-loaded; operator-authorized 2026-06-02)

*Recorded here as the operator answers, so the autonomous build runs uninterrupted.*

| Decision | Choice |
|---|---|
| Merge mode | **Merge all 6 to main** — fresh branch per PR off latest main, gated green, `gh pr merge --merge --delete-branch`, bottom-up by dependency |
| PR4 default flip | **Flip to Pure-HTTP** — new installs default to `http_handoff_http`; existing installs keep their stored preset |
| New persistent settings sign-off | **Authorized all 8** — plan defaults stand (`oppo_bdmv_checkfolder` on, `hdmi_switch_mode` immediate, autoheal on, etc.) |
| Release at end | **Cut stable release** — add-on via `/release` skill + `package.yml`, then configurator manual `npm run dist` + `gh release create` (add-on first; configurator bundles it) |

**Merge order (each branch off fresh main):** PR1 → PR2 → PR3 → PR6 → PR4 → PR5 → stable release.

## ✅ Go / 🛑 Wait / 🔁 Replan

**✅ Go — operator authorized the full autonomous build of all 6 PRs (2026-06-02).** Execution
proceeds per the answers in "Build decisions" above.
