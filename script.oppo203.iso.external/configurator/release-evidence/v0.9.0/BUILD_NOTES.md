# Configurator v0.9.0 — build notes

**Released:** 2026-06-03 · **tag:** `configurator-v0.9.0` · **commit:** `c3b8bcf`
**Built + published by:** GitHub Actions (`.github/workflows/configurator-ci.yml` → `release` job) on the tag push.
**Bundles add-on:** v2.9.15 (the configurator embeds `main`'s add-on zip via `npm run bundle:addon`).

## What shipped — the Developer Options console (umbrella #290)

A confirm-gated **Developer Options** dev surface reachable from the app header (a "Developer…" button,
hidden on dev screens, mirroring the Reset-all entry), with per-device sub-sections — **Kodi / TV /
OPPO / AVR / NAS** — each a live view + remote control, plus Kodi dev tooling and LAN scans. Seven PRs:

- **PR A** (#298) — dev-tab shell + nav (`developer` screen, 5 tabs, `steps.ts`/`App.tsx` wiring).
- **PR B-OPPO** (#299) — OPPO console: TCP `#XXX` palette (76-key map) + raw box via `oppo_query`; HTTP catalog palette via new `oppo_http_get`; live transcript with a TCP-push ⇄ HTTP-poll switch; credential endpoints redacted.
- **PR C** (#300) — Kodi dev tools: installed-vs-bundled version, settings table, register-without-restart, remote restart (`kodi_restart`), upload-any-version (`install_addon_zip`).
- **PR D-TV** (#301) — TV console: all backends + generic Sony IRCC (`tv_sony_bravia_ircc`).
- **PR D-AVR** (#302) — AVR console: all backends via existing `avr_switch_*` (0 new Rust cmds).
- **PR D-NAS** (#303) — NAS scan + protocol-detect (`scan_nas_hosts`) + share test-login (`nas_test_login`); creds never persisted/shown.
- **PR E** (#304) — Kodi LAN scan (`scan_kodi_hosts`, JSON-RPC version confirm).
- **bump** (#305) — 0.8.7 → 0.9.0.

New configurator Rust commands: `oppo_http_get`, `install_addon_zip`, `kodi_restart`,
`tv_sony_bravia_ircc`, `scan_nas_hosts`, `nas_test_login`, `scan_kodi_hosts`.

## Gates (software-verified only)

- `tsc -b` clean · **vitest 338** · **`cargo test` 50** · `vite build` clean — green on every PR and on
  the `configurator-v0.9.0` tag's CI gate.
- Each panel browser-verified in the vite dev server: navigation, command-firing, the OPPO + NAS
  **credential redaction**, and the Kodi scan.
- **Hardware validation is NOT claimed.** Nearly all device behavior (every console's TCP/HTTP/SSH I/O,
  the verbose-push + HTTP monitors, the SMB/NFS login, the LAN scans) is **Phase-C** — see
  [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](../../../docs/MANUAL_VERIFICATION_CHECKLIST.md).

## Artifacts + SHA-256

The MSI + NSIS installers and their SHA-256 sums are produced by the CI release job and attached to the
published GitHub release as `SHA256SUMS.txt` (this build is **unsigned**). Verify the download against
that file:

- https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.9.0
