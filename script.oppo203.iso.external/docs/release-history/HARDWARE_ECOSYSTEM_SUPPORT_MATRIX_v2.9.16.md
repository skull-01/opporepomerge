# Hardware Ecosystem Support Matrix — v2.9.16 Final

| Layer | Software status | Hardware validation |
|---|---|---|
| Player / OPPO / clone profiles | Preserved from v2.9.15 | Not performed / not claimed |
| Seven-option playback architecture (routing × monitor + `http_handoff_http`) | Preserved from v2.9.15; six prior presets byte-identical | Not performed / not claimed |
| AVR eligibility under the Pure-HTTP default | Fixed: `http_handoff` is AVR-eligible; power-on settle added | Not performed / not claimed |
| OPPO HTTP path translation | Fixed: translate-before-BDMV, anchored prefix rewrite, URL-encoded backslash | Not performed / not claimed |
| SVM3 / `oppo_control` / eISCP reads | Hardened: confirmed-playback timeout gate, single-`recv` + CR/LF reassembly | Not performed / not claimed |
| Pure-HTTP launch reporting | Fixed: failed activate/signin/play recorded as failed (rc=1) | Not performed / not claimed |
| Samsung TV HDMI defaults | Fixed: distinct `KEY_HDMI1` / `KEY_HDMI2` | Not performed / not claimed |
| Input coercion robustness | Fixed: `_safe_port` / `_safe_int` handle textual / non-finite values | Software behavior only |
| AutoScript generator | Hardened: `_safe_text` strips CR/LF from embedded paths/creds; configurator mirror in lock-step | Not performed / not claimed |
| TV backends / AVR framework / sequencing | Preserved from v2.9.15 | Not performed / not claimed |
| Typing / tooling | `mypy --strict` gate, ruff format, parallel tests | Software/tooling only |
| Runtime packaging | Runtime-only installable ZIP policy preserved | Software packaging only |

This software-verified support matrix separates software support from real hardware validation. Software support and real hardware validation remain separate. Do not describe a hardware path as validated unless separate real tester results are supplied.

Hardware validation remains not performed / not claimed.
