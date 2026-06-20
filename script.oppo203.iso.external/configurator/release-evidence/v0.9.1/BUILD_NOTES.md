# Configurator v0.9.1 — build notes

**Released:** 2026-06-03 · **tag:** `configurator-v0.9.1` · **commit:** `02f44bf`
**Built + published by:** GitHub Actions (`.github/workflows/configurator-ci.yml` → `release` job) on the tag push.
**Bundles add-on:** v2.9.15.

## What shipped — the AutoScript helper (umbrella #306)

A 6th Developer Options sub-section, **AutoScript**: build the player's `autoexec.sh`, check readiness,
and install it — for jailbroken stock OPPO (firmware 20X-56+) and clones.

- **PR 1** (#310) — `autoscript-gen.ts`, a **byte-exact** mirror of the add-on's `autoscript_helper.generate()`, + `capability.ts` (firmware gating + JB/clone family). Cross-language guard: `tests/test_autoscript_consistency.py` ↔ `autoscript.test.ts` both pin `autoscript-fixtures.json`.
- **PR 2** (#311) — the AutoScript panel: builder form → live `autoexec.sh` preview → readiness (`#QVR` firmware capability + family + telnet/ADB/HTTP probes + port-23 risk callout) → **export `<Desktop>/OppoKodiAddon-AutoScript/`** (`autoexec.sh` + `HOW-TO-INSTALL.txt`) via `export_autoscript_bundle`.
- **PR 3** (#312) — telnet: `autoscript_telnet_check` + confirm-gated `autoscript_push_telnet`.
- **bump** (#313) — 0.9.0 → 0.9.1.

New configurator Rust commands: `export_autoscript_bundle`, `autoscript_telnet_check`, `autoscript_push_telnet`.

## Gates (software-verified only)

- `tsc -b` clean · **vitest 356** · **`cargo test` 51** · `vite build` clean — green on every PR and the tag's CI gate.
- Add-on (PR 1's cross-language guard): `pytest -n auto` **1160/3** · **serial coverage 99%** · `ruff` clean.
- Browser-verified: the live `autoexec.sh` preview, the port-23 danger toggle, the CIFS-password redaction, and the confirm gates.
- **Hardware validation NOT claimed.** All device behavior (USB boot of the script, `#QVR`/port readiness, telnet check + push) is **Phase-C** — see [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](../../../docs/MANUAL_VERIFICATION_CHECKLIST.md).

## Artifacts + SHA-256

The MSI + NSIS installers + `SHA256SUMS.txt` are produced by the CI release job and attached to the
published GitHub release (**unsigned**). Verify against that file:

- https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.9.1
