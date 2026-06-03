# Build Notes — v2.9.16 Final

Version 2.9.16 Final is a software-verified maintenance and hardening release after the v2.9.15 Final line. It folds in the correctness and robustness fixes merged since v2.9.15 — AVR sequencing under the Pure-HTTP default, OPPO HTTP path translation, monitor/transport read hardening, configurator-owned settings schema guards, honest Pure-HTTP launch failures, distinct Samsung HDMI defaults, and two property-test passes that fixed real coercion crashes — plus one cross-area AutoScript generator hardening. No protected playback behavior changed and the seven playback-architecture presets stay byte-identical.

## Scope

- **AVR / Pure-HTTP correctness (#221–#224).** AVR power-on/input/restore are no longer silently skipped when the default `http_handoff` routing is active (`http_handoff` is now AVR-eligible); OPPO HTTP path translation runs before the BDMV check with an anchored prefix rewrite; an AVR power-on settle delay was added; backslashes are URL-encoded in HTTP paths.
- **Monitor / transport hardening (#226–#233).** The SVM3 startup timeout is gated on confirmed playback rather than device chatter; `oppo_control` and the eISCP AVR driver use single-`recv` buffering with CR/LF reassembly; the ADB live-test passes a `Settings` object; the clone-wake import is package-relative; a `LOADING` state is no longer treated as confirmed playback; a fall-back status snapshot is written.
- **Settings schema guards (#235–#237).** The six configurator-owned settings are declared in `DEFAULTS` + `settings.xml` with an emitted-vs-read guard test; an AVR backend-id guard was added; stale six→seven preset comments were corrected.
- **Honest Pure-HTTP launch (#254).** `_start_oppo_http` drops the blanket `try/except` so a failed `activate → signin → play` is recorded as `failed` (rc=1) instead of a silent success.
- **Distinct Samsung HDMI defaults (#256).** The Samsung TV switch now uses distinct `KEY_HDMI1` / `KEY_HDMI2` defaults for the two switch directions.
- **Coercion-crash fixes (#275, #329).** Two property-test passes (`tests/test_property_http_hdmi.py`, `tests/test_property_addon_robustness.py`, Hypothesis-or-fallback) found and fixed real crashes: an `OverflowError` on `int(float("inf"))` in `http_info_indicates_playing`, and four `int()` port/option crashes on textual (`"8060/tcp"`) or non-finite ports from device-cache JSON, an mDNS record, or a JSON AutoScript preset (new `discovery._safe_port` + `autoscript_helper._safe_int`).
- **AutoScript generator hardening (cross-area, this release).** `autoscript_helper.generate()` now strips CR/LF from the embedded path/credential fields (`heartbeat_path`, mount paths/options, CIFS user/pass) via a new `_safe_text`, so a value carrying a carriage return can no longer inject a CR (BusyBox sh on the OPPO chokes on CRLF) or split a directive across lines. The configurator's byte-exact mirror `configurator/src/autoscript/autoscript-gen.ts` gets the identical `safeText`, a new `crlf_paths` fixture pins the behavior on both sides, and the cross-language guards (`tests/test_autoscript_consistency.py` + `configurator/src/autoscript/autoscript.test.ts`) stay green. Surfaced by the #330 property test; same class as #275/#329. A latent mypy `--strict` finding in `discovery._safe_port` (`int()` on `object`) was also corrected with a behavior-preserving cast.

## Preserved behavior

- The core protected behaviors remain unchanged: 4K/UHD disc-style interception only, loose/raw files stay with Kodi, conservative `playercorefactory.xml` routing, the canonical OPPO command map with no forbidden tokens (`#SIS`/`#PGU`/`#PGD`), NAS/AutoScript behavior, the Kodi startup auto-power guard, TV switching, and AVR sequencing.
- The runtime-only installable ZIP policy remains preserved.
- The seven-preset matrix stays a maintained cross-area contract (add-on `PLAYBACK_ARCHITECTURE_PRESETS` ↔ configurator routing/monitor enums), guarded by the cross-language `tests/test_playback_presets_consistency.py`; the six prior presets stay byte-identical.

## Hardware validation

This is a software-verified release. Real hardware validation was not performed or claimed.
