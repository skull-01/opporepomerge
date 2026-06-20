# MVP Compliance Matrix - Version 2.0.0 Build 4

This matrix records the v2.0 MVP status after Build 4. It is intended to be readable by a local AI model and by a human release reviewer.

| MVP requirement | Build 4 status | Evidence / notes |
|---|---|---|
| External Player flow only for MVP | Met | Visible architecture-selection settings remain deferred; MVP path uses `external_player.py`. |
| M9702 / Chinoppo wake support | Met | Clone profiles rewrite `#PON` / `#POW` to `#EJT`. |
| Stock OPPO behavior preserved | Met | UDP-203/UDP-205 keep `#PON` and `#POW` unchanged. |
| TCL / Android TV HDMI switching through ADB | Met for MVP | TV switch-to-OPPO and switch-back are settings-controlled and non-fatal. Real hardware is recorded as user-assumed passed. |
| Basic OPPO TCP command path | Met | Existing OPPO TCP command path and fake OPPO loopback tests are retained. |
| Session sentinel cleanup | Met | Tests verify cleanup on failure paths. |
| Minimal MVP settings | Met | OPPO host/port, hardware model, external player path, TV/ADB switching, start commands, and stop commands are present. |
| Kodi remote bridge where already functional | Met | Canonical 76-key command map is retained. |
| Tests for MVP behavior | Met | Unit and integration-style loopback tests pass without real OPPO, TV, or ADB. |
| Fake OPPO server tests | Met | Loopback fake server supports `@OK`, `@ER`, `@UPL`, `@UPW`, and disconnect behavior. |
| Kodi stubs | Met as staged foundation | Local test-only stubs exist for `xbmc`, `xbmcaddon`, `xbmcgui`, `xbmcvfs`, `xbmcplugin`, and `xbmcdrm`. |
| 92% coverage gate | Staged / deferred | `.coveragerc` restored with historical 85% target; final 92% gate remains future hardening. |
| README/reference/web-references synchronized | Met | Build 4 sections added to all three docs. |
| Manual physical-hardware validation | Recorded as assumed passed | User instructed that latest build was tested on real hardware with no issues found. |

## Release-candidate posture

Build 4 is suitable for release-candidate review of the MVP scope, subject to the user's decision on whether to keep the staged 92% coverage gate as a post-MVP hardening item.

## Still intentionally deferred from v2.0 MVP

- Full v1.3-style superset merge.
- Full discovery dashboard.
- Full diagnostics dashboard.
- Full wizard polish restoration.
- Reavon command-map support.
- Repository submission finalization.
