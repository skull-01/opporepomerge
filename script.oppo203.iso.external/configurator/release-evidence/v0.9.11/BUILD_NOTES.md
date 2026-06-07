# Configurator v0.9.11 — Build Notes

**Theme:** follow-up fix to v0.9.10's per-device ping, found during hardware testing.

**Bundled add-on:** v2.9.17 (unchanged). **Hardware validation:** software-verified only; not
performed / not claimed.

## What changed

- **KodiPanel ping uses an editable Kodi box IP** (PR #360, merge `7ebac02`). The Kodi dev panel
  had no editable box-IP field — the Ping used `state.kodiIp` (default `10.0.1.42`) while the only
  visible field was the scan *Base IP*, so it pinged the stale default instead of the IP you typed.
  Added an editable **"Kodi box IP"** field that the Ping + all panel ops use; restructured the
  subnet scan as a secondary "Don't know the IP? Scan the subnet" helper; dropped the fake
  `10.0.1.42` `kodiIp` default to empty (matches `tvIp`). The dashboard kodi node now reads
  no-address until an IP is set.

## Gate (software-verified)

- `npx tsc --noEmit` — clean
- `npx vitest run` — **361 passed**
- `cargo test` — **57 passed**
- `npm run dist` (MSI + NSIS) — built for this release

## Artifacts

- `Kodi Oppo External Player Configurator_0.9.11_x64_en-US.msi`
- `Kodi Oppo External Player Configurator_0.9.11_x64-setup.exe` (NSIS)
- `SHA256SUMS.txt`

Published via `scripts/release-configurator-local.ps1` as `configurator-v0.9.11` (repo Latest).
