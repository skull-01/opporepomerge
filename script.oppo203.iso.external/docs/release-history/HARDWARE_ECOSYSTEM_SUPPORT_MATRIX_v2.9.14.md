# Hardware Ecosystem Support Matrix — v2.9.14 Final

| Layer | Software status | Hardware validation |
|---|---|---|
| Player / OPPO / clone profiles | Preserved from v2.9.13 | Not performed / not claimed |
| Six-option playback architecture (routing × monitor) | New: `playercorefactory`/`service_interception`/`http_handoff` × `legacy`/`svm3`, one dispatch | Not performed / not claimed |
| SVM3 verbose-mode monitor (`#SVM 3`) | New: confirms playback/progress from `@UPL`/`@UTC`, legacy fallback | Not performed / not claimed |
| Richer session status (`oppo203iso-status.json`) | New: `session_id`/timestamps/phase + heartbeat (additive) | Software behavior only |
| Hold-mode robustness | `tcp_qpl_poll` default, bounded timeouts, sentinel self-heal | Not performed / not claimed |
| TV backends and presets | Preserved from v2.9.13 (`tv_*` module rename) | Not performed / not claimed |
| AVR framework and drivers | Preserved from v2.9.13 | Not performed / not claimed |
| Unified TV + AVR sequencing | Preserved from v2.9.13 | Not performed / not claimed |
| Typing / tooling | `mypy --strict` gate (54 files), ruff format, parallel tests | Software/tooling only |
| Runtime packaging | Runtime-only installable ZIP policy preserved | Software packaging only |

This software-verified support matrix separates software support from real hardware validation. Software support and real hardware validation remain separate. Do not describe a hardware path as validated unless separate real tester results are supplied.

Hardware validation remains not performed / not claimed.
