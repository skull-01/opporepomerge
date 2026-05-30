# Configurator v0.5.0 — AVR Step 5 wired into add-on settings

**Built:** 2026-05-30 · **Source:** `main` (Tauri 2 + React/TS configurator) ·
**Status:** software-verified only; **unsigned**; no hardware validation.

The fifth Windows binary of the OppoKodiAddon Configurator, tag `configurator-v0.5.0`.
Follow-up to v0.4.0 (which added the AVR database + an advisory Step 5): the receiver
selection now **flows into the add-on's settings.xml**, giving Step 5 parity with the TV and
Player steps.

- **Step 5 captures receiver IP + player input** (a "Receiver control" card shown once a model
  is picked) and `mapping.ts` emits `avr_backend` / `avr_host` / `avr_player_input` +
  `avr_control_enabled`.
- **Backend mapping** (`avrAddonBackend()`, verified against
  `resources/lib/avr/avr_presets.py`): the DB's `onkyo_eiscp` splits to the add-on's distinct
  `pioneer_eiscp` for Pioneer; `sony_audio` → `sony_audio_api`.
- **Conservative enable.** Control auto-enables only for a native, non-gated driver
  (Denon/Marantz, Yamaha, Onkyo/Integra, Pioneer) with host + player input present. Sony is
  configured but left **disabled** (add-on gates it on acknowledgement + PSK). `custom_command`
  brands (Anthem/Arcam/NAD) write no `avr_backend`. Skipping Step 5 writes nothing AVR-related.

No add-on code change; the add-on already ships these settings + guarded drivers. The settings
merge preserves any AVR settings the configurator doesn't own.

## Artifacts

| Artifact | Size | SHA-256 |
|---|---|---|
| `OppoKodiAddon Configurator_0.5.0_x64_en-US.msi` (MSI) | 3,174,400 B | `60283a0240afd0aa745a9fa5d853e125a6558572fcd269b911c90b3ab0792742` |
| `OppoKodiAddon Configurator_0.5.0_x64-setup.exe` (NSIS) | 2,071,403 B | `8022844316ee8c25e0463f3334d9148376fd97fec9c9f7e60f46052d4dc4a709` |

Verify after download (PowerShell): `Get-FileHash <file> -Algorithm SHA256`. The published
release assets were re-downloaded and confirmed byte-identical to this build.

## Build environment

- Windows 11 (x64) · Node v24.15.0 / npm 11.12.1 · Rust / cargo 1.95.0 (MSVC)
- Tauri CLI 2 — `npm run dist`; `bundle.targets: "all"` → MSI (WiX) + NSIS setup

## Caveats

- **Unsigned** — SmartScreen "unknown publisher" expected on install.
- **Software-verified only.** `tsc` + `npm run build` + **101 vitest** (22 mapping tests);
  Step 5's Pioneer and Sony paths exercised in a browser preview. Not installed on a clean
  machine; **no hardware validation**.
- **Enabling AVR control means the add-on will try to power on + switch the receiver on
  handoff.** All backend/input mappings are `validated:false` candidates — confirm against
  the real receiver. Most receivers need Network Standby / IP Control enabled.

## Phase C — operator end-to-end (clean Windows host)

1. Install from the `configurator-v0.5.0` release; confirm SHA-256 matches the table.
2. Step 5 → "Yes" → pick a brand + model; confirm the **Receiver control** card appears with
   IP + player-input fields, and that filling both shows the green "we'll enable" callout
   (Sony instead shows the "left off, needs ack + PSK" warning; Anthem/Arcam/NAD show the
   "no native backend" note).
3. Run the final apply (Tier A/B/C) and confirm the generated `addon_data/.../settings.xml`
   carries `avr_backend` / `avr_host` / `avr_player_input` / `avr_control_enabled` as
   expected — and that skipping Step 5 leaves any existing AVR settings untouched.
