# Configurator v0.9.13 — Build Notes

**Theme:** CEC tab follow-ups — claim the TV from an **already-on** OPPO, and an **SSH-key auth
helper** for the Kodi claim.

**Bundled add-on:** v2.9.17 (unchanged). **Hardware validation:** software-verified only; not
performed / not claimed.

## What changed (PR #364, merge `638e700`)

- **OPPO "force claim" for an already-on player.** A plain wake (#EJT/#PON) only asserts CEC active
  source on power-*up*, so an already-on OPPO won't re-claim the TV. Added two force options: a
  **power cycle** (#POF → 4s → #PON, which re-fires One Touch Play) and **Play (#PLA)** (asserts
  active source via playback). The standby wake buttons remain.
- **SSH-key authorization helper** in the Kodi section. The Kodi claim runs Kodi's
  `CECActivateSource` over **key-only** SSH (no password), which fails with "Permission denied" until
  the host key is authorized. The helper adds **Test SSH**, shows (or **generates**) the Windows
  public key via a new `ssh_public_key` command, and gives the exact copy-paste install command to
  append it to the box's `authorized_keys`.

## Gate (software-verified)

- `npx tsc --noEmit` — clean
- `npx vitest run` — **361 passed**
- `cargo test` — **57 passed**
- `npm run dist` (MSI + NSIS) — built for this release

## Artifacts

- `Kodi Oppo External Player Configurator_0.9.13_x64_en-US.msi`
- `Kodi Oppo External Player Configurator_0.9.13_x64-setup.exe` (NSIS)
- `SHA256SUMS.txt`

Published via `scripts/release-configurator-local.ps1` as `configurator-v0.9.13` (repo Latest).
