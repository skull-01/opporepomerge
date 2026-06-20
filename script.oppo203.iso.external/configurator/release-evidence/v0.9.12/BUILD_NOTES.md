# Configurator v0.9.12 — Build Notes

**Theme:** a **CEC ownership-claim** tab in Developer Options — the HDMI-switching behaviour test.

**Bundled add-on:** v2.9.17 (unchanged). **Hardware validation:** software-verified only; not
performed / not claimed.

## What changed

- **CEC tab in Developer Options** (PR #362, merge `ee942af`). A behaviour test for HDMI switching
  that triggers each device's *native* CEC active-source claim (the configurator sends no CEC
  frames itself) and the operator watches the TV:
  - **OPPO → claim TV:** editable OPPO IP + ping; **Wake clone (#EJT)** / **Power on (#PON)** via
    `oppo_power`. On wake the OPPO asserts CEC active source → the TV should switch to the player.
  - **Kodi → claim TV:** editable Kodi IP + ping; new **`kodi_cec_activate`** command runs
    `kodi-send --action=CECActivateSource` over SSH → Kodi asserts active source → the TV should
    switch back to the Kodi box.
  - A shared transcript logs each command + reply; the actual HDMI switch is observed on the TV
    (CEC exposes no telemetry to read back).

## Gate (software-verified)

- `npx tsc --noEmit` — clean
- `npx vitest run` — **361 passed**
- `cargo test` — **57 passed**
- `npm run dist` (MSI + NSIS) — built for this release

## Artifacts

- `Kodi Oppo External Player Configurator_0.9.12_x64_en-US.msi`
- `Kodi Oppo External Player Configurator_0.9.12_x64-setup.exe` (NSIS)
- `SHA256SUMS.txt`

Published via `scripts/release-configurator-local.ps1` as `configurator-v0.9.12` (repo Latest).
