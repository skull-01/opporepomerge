# Configurator v0.9.14 — Build Notes

**Theme:** CEC tab — **play a real test file** to test CEC-on-play.

**Bundled add-on:** v2.9.17 (unchanged). **Hardware validation:** software-verified only; not
performed / not claimed.

## What changed (PR #366, merge `eadd704`)

- **"Play a real file" action** in the CEC tab's OPPO section. Enter an OPPO-visible path and it
  fires `oppo_http_play` (`/playnormalfile` — the same activate → signin → play the add-on's handoff
  makes). Starting playback is the only CEC trigger (there is **no direct CEC command** on the OPPO —
  the TCP catalog has `#SRC`/`#QHD` for the player's own HDMI input, not the TV), so this tests
  whether the OPPO asserts CEC active source on play → the TV switches to it. If it does, the add-on's
  normal handoff already does this on every play, so switching is automatic with no TV backend.

## Gate (software-verified)

- `npx tsc --noEmit` — clean
- `npx vitest run` — **361 passed**
- `cargo test` — **57 passed**
- `npm run dist` (MSI + NSIS) — built for this release

## Artifacts

- `Kodi Oppo External Player Configurator_0.9.14_x64_en-US.msi`
- `Kodi Oppo External Player Configurator_0.9.14_x64-setup.exe` (NSIS)
- `SHA256SUMS.txt`

Published via `scripts/release-configurator-local.ps1` as `configurator-v0.9.14` (repo Latest).
