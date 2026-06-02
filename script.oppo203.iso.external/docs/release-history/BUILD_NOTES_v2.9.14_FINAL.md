# Build Notes — v2.9.14 Final

Version 2.9.14 Final is a software-verified release after the v2.9.13 Final line. It completes the six-option playback-architecture matrix, adds an SVM3 verbose-mode playback monitor and richer session status, and hardens playback robustness.

## Scope

- **Six-option playback architecture.** Three routing modes (`playercorefactory`, `service_interception`, `http_handoff`) by two monitor modes (`legacy`, `svm3`) — six runtime presets in one package, all sharing a single dispatch in `run_playback_session` (`resources/lib/kodi/playback_session.py`). `normalize_architecture()` resolves the chosen preset from `playback_architecture_preset`; the configurator emits it. The set is pinned by `tests/test_architecture_presets.py`.
- **SVM3 monitor.** `resources/lib/oppo/playback_monitor_svm3.py` (`OppoSvm3PlaybackMonitor`) — a persistent `#SVM 3` verbose-mode client that confirms real playback and progress from `@UPL PLAY` and advancing `@UTC` frames, with automatic legacy fallback on connect failure.
- **Richer session status (Phase 5.1).** `oppo203iso-status.json` now carries a stable `session_id`, `started_at`/`updated_at` timestamps, and a `launching` → `monitoring` → `ended` phase with a mid-session heartbeat. New fields are additive and optional.
- **Robustness hardening.** The default `hold_mode` is `tcp_qpl_poll` so a stopped disc is detected; hold modes are bounded with timeouts; a stale `oppo203iso-active` session sentinel now self-heals.
- **Supporting work since v2.9.13.** Read-only OPPO status probe (`#Q..` queries); `tv_*` module rename for parity with `avr_*`; ENH-#51 incremental `mypy --strict` gate across `resources/lib`; ENH-#42 in-add-on network-settings and language menus; `resources/lib` split into `tv`/`oppo`/`avr`/`kodi` sub-packages with a lazy deprecation-window compatibility finder.

## Preserved behavior

- The core protected behaviors remain unchanged: 4K/UHD disc-style interception only, loose/raw files stay with Kodi, conservative `playercorefactory.xml` routing, the canonical OPPO command map with no forbidden tokens (`#SIS`/`#PGU`/`#PGD`), NAS/AutoScript behavior, the Kodi startup auto-power guard, TV switching, and AVR sequencing.
- The runtime-only installable ZIP policy remains preserved.
- The six-preset matrix is a maintained cross-area contract (add-on `PLAYBACK_ARCHITECTURE_PRESETS` ↔ configurator routing/monitor enums), additionally guarded by the cross-language `tests/test_playback_presets_consistency.py`.

## Hardware validation

This is a software-verified release. Real hardware validation was not performed or claimed.
