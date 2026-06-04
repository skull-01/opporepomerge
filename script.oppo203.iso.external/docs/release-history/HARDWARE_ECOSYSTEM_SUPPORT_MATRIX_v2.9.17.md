# Hardware Ecosystem Support Matrix — v2.9.17 Final

| Layer | Software status | Hardware validation |
|---|---|---|
| Player / OPPO / clone profiles | Extended: +5 clone variants (M9205 V2/V3/V4, M9702 Plus, VenPro V203), mirroring base control | Not performed / not claimed |
| `oppo_hardware_model` enum | Appended (positional, install-base-safe); 18 → 23 models | Not performed / not claimed |
| Dolby Vision capability layer | Added: per-player capable/tv_led/player_led/confidence + global TV rule (advisory, data-only) | Not performed / not claimed |
| Cross-area players-DB drift guard | Extended: JSON ↔ add-on registry pinned for taxonomy + Dolby Vision | Software guard only |
| Seven-option playback architecture (routing × monitor + `http_handoff_http`) | Preserved from v2.9.16; byte-identical | Not performed / not claimed |
| Canonical OPPO command map / forbidden tokens | Preserved from v2.9.16 | Not performed / not claimed |
| TV backends / AVR framework / sequencing | Preserved from v2.9.16 | Not performed / not claimed |
| Typing / tooling | `mypy --strict` gate, ruff format, parallel tests | Software/tooling only |
| Runtime packaging | Runtime-only installable ZIP policy preserved | Software packaging only |

This software-verified support matrix separates software support from real hardware validation. The new clone variants and Dolby Vision stances are research-sourced; do not describe a hardware path as validated unless separate real tester results are supplied.

Hardware validation remains not performed / not claimed.
