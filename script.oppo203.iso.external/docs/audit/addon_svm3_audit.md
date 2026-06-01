# Addon SVM3 + verify-played audit + Phase-C runbook

**Scope:** the SVM3 four-option enhancement issues (#150 / #151 / #152) and the verify-played
enhancement (#113), whose code is merged to `main`. As with the robustness audit, this confirms
each fix at a `file:line` pinned by a passing test, then gives the on-device **Phase-C** steps the
operator runs to verify and close.

**"Confirmed fixed in code" ≠ hardware-validated.** SVM3 in particular asserts a hardware protocol
contract (`#QVM` / `#SVM 3` / `@UPL` / `@UTC`) that **cannot** be proven without a real OPPO. The
Phase-C steps below are the only thing that validates that contract.

**Audited from `main` (this session re-ran the tests):** `pytest tests/test_architecture_presets.py
tests/test_svm3_playback_monitor.py tests/test_playback_session_modes.py` → **69 passed**. No
`resources/` code was changed by this audit (docs only).

## Summary

| Issue | What | Merged | Code anchor | Pinned by | Status |
|---|---|---|---|---|---|
| #150 | `playback_monitor_mode` + four-option preset mapping | #143 `fadd8c9` | `architecture_preset` / `normalize_architecture` ([settings_reader.py:248](../../resources/lib/kodi/settings_reader.py#L248)) | `test_architecture_presets.py` | ✅ fixed in code |
| #151 | SVM3 OPPO playback monitor | #144 `ccf3638` | `OppoSvm3PlaybackMonitor` ([playback_monitor_svm3.py:243](../../resources/lib/oppo/playback_monitor_svm3.py#L243)) | `test_svm3_playback_monitor.py` | ✅ fixed in code |
| #152 | shared `run_playback_session` engine | #145 `421c2f0` | `run_playback_session` ([playback_session.py:143](../../resources/lib/kodi/playback_session.py#L143)) | `test_playback_session_modes.py` | ✅ fixed in code |
| #113 | verify playback actually started | #144/#145 (via SVM3) | `confirmed_playback` / `confirmed_progress` ([playback_monitor_svm3.py:248](../../resources/lib/oppo/playback_monitor_svm3.py#L248), [:267](../../resources/lib/oppo/playback_monitor_svm3.py#L267)) | `test_svm3_playback_monitor.py` | ⚠️ realized for SVM3; **partial** for legacy |

**Audit conclusion:** #150/#151/#152 are genuinely addressed in code. **#113 is the one to read
carefully** — SVM3 fully realizes positive playback confirmation, but the legacy hold path still
only *holds* (no positive confirmation). See its note before deciding whether to close #113 or keep
it open for the legacy path. All remain **open** pending Phase C.

---

## #150 — `playback_monitor_mode` + four-option preset mapping

- **Fix (`#143` `fadd8c9`):** adds the monitor axis `playback_monitor_mode` (`legacy`|`svm3`) and the pure resolvers `architecture_preset(routing, monitor)` + `normalize_architecture(settings)` — [settings_reader.py:248-263](../../resources/lib/kodi/settings_reader.py#L248) — producing the four combined presets. Reader-only; the combined `playback_architecture_preset` is the configurator-written source of truth **when present** and is deliberately **not** in `DEFAULTS` (so it can't mask a pre-existing `service_interception` install — it's derived from the legacy fields when absent).
- **Phase C (on the box):** deploy a config from the wizard with a known Playback mode, then inspect the resolved values in the add-on log / settings. **Expect:** an existing `external_player` install resolves to `playercorefactory_legacy`, `service_interception` → `service_interception_legacy`, and an SVM3 config → the matching `*_svm3` preset; nothing acts differently at runtime from the preset alone (it selects the monitor in #152). **Record:** the resolved `playback_architecture_preset` + `playback_monitor_mode` for each config tried.

## #151 — SVM3 OPPO playback monitor

- **Fix (`#144` `ccf3638`):** `OppoSvm3PlaybackMonitor` — a persistent `#SVM 3` client that confirms playback **only** from OPPO events: `@UPL PLAY` → `confirmed_playback` ([playback_monitor_svm3.py:248](../../resources/lib/oppo/playback_monitor_svm3.py#L248)), an *advancing* `@UTC` → `confirmed_progress` ([:267](../../resources/lib/oppo/playback_monitor_svm3.py#L267)) — never from a sent command; restores the prior verbose mode on exit.
- **Phase C (on a real OPPO UDP-203/205):** during an SVM3-mode playback, confirm `#QVM` returns the current mode, `#SVM 3` is **accepted**, `@UPL`/`@UTC` frames arrive during playback, and the previous verbose mode is **restored** on exit. On **Chinoppo clones**, confirm `#SVM 3` is either accepted or **fails honestly** (the monitor falls back — see #152). **Record:** the `#QVM`/`#SVM 3` replies, whether `@UPL`/`@UTC` arrived, and the restored mode.

## #152 — shared `run_playback_session` engine

- **Fix (`#145` `421c2f0`):** `run_playback_session` ([playback_session.py:143](../../resources/lib/kodi/playback_session.py#L143)) is the single sequence both entry points use: legacy → the existing `hold_playback`; svm3 → `OppoSvm3PlaybackMonitor`, **falling back to the legacy hold if it cannot connect**. Writes a split-truth `oppo203iso-status.json`.
- **Phase C (on the box, end-to-end, each preset):** legacy presets → behavior unchanged (the chosen `hold_mode` ends the hold). SVM3 presets → the OPPO confirms via `@UPL`/`@UTC`, prior verbose mode restored, and `oppo203iso-status.json` shows `confirmed_playback`/`confirmed_progress`. SVM3 with an unreachable control port → **falls back to the legacy hold** (no hang). **Record:** for each preset, the status-JSON contents + that the legacy path is byte-for-byte the same call sequence.

## #113 — verify playback actually started (read carefully)

- **Realized by SVM3 (`#144`/`#145`):** the original ask was to positively verify the OPPO *started* playing (rather than blindly hold). For `monitor_mode=svm3` this is now true: `confirmed_playback`/`confirmed_progress` are set only from real OPPO push events and surfaced in `oppo203iso-status.json`.
- **⚠️ Gap to decide:** the **legacy** monitor path does **not** positively confirm playback — it still just holds (timeout / file / `#QPL` idle-poll). So #113 is **fully satisfied only for the SVM3 path**. The legacy hold modes detect *stop*, not *start*.
- **Phase C + close decision:** verify the SVM3 path reports `confirmed_playback=true` for a real successful play and `false` for a failed start (e.g. start with no disc). Then **decide**: close #113 as satisfied-by-SVM3 (legacy is explicitly "compatibility, hold-only"), or keep it open scoped to "positive start-confirmation for the legacy path." This audit recommends the former, with a one-line note on the issue that legacy stays hold-only by design. **Record:** the SVM3 confirmed flags for a good vs failed start.
