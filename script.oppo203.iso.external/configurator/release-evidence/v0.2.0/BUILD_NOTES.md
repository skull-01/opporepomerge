# Configurator v0.2.0 — wizard rename + design-review pass

**Built:** 2026-05-30 · **Source:** `main` (Tauri 2 + React/TS configurator) ·
**Status:** software-verified only; **unsigned**; no hardware validation.

The second Windows binary of the OppoKodiAddon Configurator, distributed as the
GitHub release tagged `configurator-v0.2.0`. It ships the wizard rename + the
design-review pass (PR #99): screen files / ids / components / labels now match
the displayed step numbers (Player = step 2, TV = step 3, HDMI Input = step 4),
the reordered stepper/chain (ISO Playback → Kodi → Player → TV), colored brand
badges drawn from real brand marks (`simple-icons`), the Step 0 "Ideal
preparations" table, and the Tier A "SSH can be disabled after setup" note.
UI/flow only — no Rust, settings, or mapping/generate changes.

The binaries are not committed (`target/` is git-ignored); this file records
their identity so the release artifacts are verifiable.

## Artifacts

| Artifact | Size | SHA-256 |
|---|---|---|
| `OppoKodiAddon Configurator_0.2.0_x64_en-US.msi` (MSI) | 3,162,112 B | `202d79e7eb28c347fb2746a48932f2cb0365bcf6b1d48f9d695cfd6caedc0765` |
| `OppoKodiAddon Configurator_0.2.0_x64-setup.exe` (NSIS) | 2,059,233 B | `2c0bd3abf3b360b70912a00ae02741f5af49d03a509234ee57ec1c18558468d0` |

Verify after download (PowerShell): `Get-FileHash <file> -Algorithm SHA256`.

## Build environment

- Windows 11 (x64)
- Node v24.15.0 / npm 11.12.1
- Rust / cargo 1.95.0 (MSVC toolchain)
- Tauri CLI 2 — `npm run dist` (= `tauri build`); see [`configurator/BUILD.md`](../../BUILD.md)
- `bundle.targets: "all"` → MSI (WiX) + NSIS setup

## Caveats

- **Unsigned.** Windows SmartScreen shows an "unknown publisher" warning on
  install. Expected for a 0.x release; code signing is a future enhancement.
- **Software-verified only.** The app builds, typechecks (`tsc`), and passes 64
  unit tests; it has **not** been validated against a real Kodi box / OPPO / TV,
  nor installed/launched on a clean Windows machine by the maintainers — that is
  the operator's Phase C below.
- **Brand-icon fallbacks.** `simple-icons` 16.x does not carry TCL, Hisense, or
  Vizio, so those TV brands render the generic device glyph (by design). The Sony
  mark is white on its white badge (a cosmetic issue flagged in PR #99 for a
  follow-up); it does not affect function.

## Phase C — operator end-to-end (clean Windows host)

1. Download the MSI (or NSIS `-setup.exe`) from the `configurator-v0.2.0`
   release; confirm its SHA-256 matches the table above.
2. Run the installer. Confirm the SmartScreen "unknown publisher" prompt is the
   only warning and that it installs without error.
3. Launch the app; confirm the window opens (custom frameless title bar,
   1180×820) and the configurator UI renders.
4. Click through the wizard: Step 0 → Kodi (1) → **Player (2) → TV (3)** → HDMI
   Input (4) → Playback Test; confirm the stepper/chain order and that brand
   badges render (real marks for OPPO / Sony / Samsung / LG / Roku / Panasonic,
   device glyph for the rest).
5. Uninstall via Apps & features (or the MSI); confirm clean removal.
