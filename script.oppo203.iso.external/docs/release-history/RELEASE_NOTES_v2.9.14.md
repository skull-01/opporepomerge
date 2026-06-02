# Release Notes — v2.9.14 Final

This release completes the six-option playback-architecture matrix, adds an SVM3 verbose-mode playback monitor and richer session status, and hardens playback robustness for the software-verified Kodi add-on.

## Highlights

- Six playback presets in one package: three routing modes (`playercorefactory`, `service_interception`, `http_handoff`) by two monitor modes (`legacy`, `svm3`), all sharing one dispatch in `run_playback_session`.
- SVM3 (`#SVM 3`) verbose-mode playback monitor confirms real playback and progress from `@UPL` and `@UTC` frames, with automatic legacy fallback on connect failure.
- Richer `oppo203iso-status.json` session report: a stable `session_id`, `started_at`/`updated_at` timestamps, and a `launching` → `monitoring` → `ended` phase with a mid-session heartbeat (additive optional fields for the configurator's live dashboard).
- Robustness hardening: the default hold mode is `tcp_qpl_poll` so a stopped disc is detected, hold modes are bounded with timeouts, and a stale session sentinel self-heals.
- Supporting work since v2.9.13: read-only OPPO status probe; `tv_*` module rename for parity with `avr_*`; incremental `mypy --strict` gate (ENH-#51); in-add-on network/language menus (ENH-#42); `resources/lib` sub-package split.

## Runtime behavior

Runtime behavior changed in v2.9.14. The playback dispatch now supports the six routing-by-monitor presets and the SVM3 monitor, the default hold mode is `tcp_qpl_poll`, hold modes are bounded with timeouts, and the session sentinel self-heals. These are additive and bug-fix changes; an existing install keeps the legacy preset derived from its current settings unless the configurator writes a new preset. The core protected behaviors are preserved: 4K/UHD disc-style interception only, loose/raw files stay with Kodi, conservative `playercorefactory.xml` routing, the canonical OPPO command map with no forbidden tokens, NAS/AutoScript behavior, startup auto-power, TV switching, and AVR sequencing.

## Hardware validation

This package remains software-verified only. Hardware validation is not performed / not claimed.
