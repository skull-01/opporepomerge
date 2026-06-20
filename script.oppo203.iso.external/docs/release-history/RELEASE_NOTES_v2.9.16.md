# Release Notes — v2.9.16 Final

Version 2.9.16 Final is a software-verified maintenance and hardening release that folds in the correctness and robustness fixes merged since v2.9.15. No new playback presets or persistent-setting categories are added; the seven-preset matrix and the protected playback behaviors stay intact.

## Highlights

- **AVR fires under the Pure-HTTP default** — AVR power-on/input/restore are no longer skipped when the default `http_handoff` routing is active (`http_handoff` is now AVR-eligible), with an added power-on settle delay.
- **OPPO HTTP path translation** — the configured path translation runs before the BDMV check, with an anchored prefix rewrite and URL-encoded backslashes.
- **Monitor and transport hardening** — the SVM3 startup timeout is gated on confirmed playback, `oppo_control`/eISCP reads use single-`recv` buffering with CR/LF reassembly, and a `LOADING` state is no longer treated as confirmed playback.
- **Settings schema guards** — the six configurator-owned settings are declared with an emitted-vs-read guard; an AVR backend-id guard was added.
- **Honest Pure-HTTP launch** — a failed `activate → signin → play` is now reported as failed (rc=1) instead of a swallowed success.
- **Distinct Samsung HDMI defaults** — `KEY_HDMI1` / `KEY_HDMI2` are now distinct for the two switch directions.
- **Coercion-crash fixes** — two property-test passes fixed an `OverflowError` on `int(inf)` in `http_info_indicates_playing` and four `int()` port/option crashes in discovery and AutoScript parsing.
- **AutoScript CR/LF hardening** — the AutoScript generator now strips carriage returns / newlines from embedded paths and credentials, so a stray CR can no longer corrupt the generated `autoexec.sh`; the configurator's byte-exact mirror is updated in lock-step.

## Runtime behavior

Runtime behavior changed in v2.9.16 only on the previously-broken or unsafe paths described above (AVR eligibility under the Pure-HTTP default, HTTP path translation ordering, monitor/transport reads, launch-failure reporting, Samsung HDMI defaults, input coercion, and AutoScript text sanitization). The seven playback-architecture presets, the playback dispatch, the canonical OPPO command map, conservative `playercorefactory.xml` routing, NAS/AutoScript behavior, startup auto-power, TV switching, and AVR sequencing are otherwise preserved; the six prior presets stay byte-identical.

## Hardware validation

This package remains software-verified only. The AVR, OPPO HTTP, monitor/transport, switching, and AutoScript paths these fixes touch are firmware- and device-dependent; hardware validation is not performed / not claimed.
