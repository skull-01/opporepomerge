# Configurator v0.1.0 — first Windows binary

**Built:** 2026-05-30 · **Source:** `main` (Tauri 2 + React/TS configurator) ·
**Status:** software-verified only; **unsigned**; no hardware validation.

This records the **first official Windows binary** of the OppoKodiAddon
Configurator, distributed as a GitHub pre-release tagged `configurator-v0.1.0`.
The binaries are not committed (`target/` is git-ignored); this file records
their identity so the release artifacts are verifiable.

## Artifacts

| Artifact | Size | SHA-256 |
|---|---|---|
| `OppoKodiAddon Configurator_0.1.0_x64_en-US.msi` (MSI) | 3,153,920 B | `ff727ea941f38b67ff79cfb3ecd01d19b51df47c9bc199f481ee619c8ff19444` |
| `OppoKodiAddon Configurator_0.1.0_x64-setup.exe` (NSIS) | 2,052,249 B | `218aa24a026b5349bcd4db41b4b053737472909d93593954dbdb84dc77b81f28` |

Verify after download (PowerShell): `Get-FileHash <file> -Algorithm SHA256`.

## Build environment

- Windows 11 (x64)
- Node v24.15.0 / npm 11.12.1
- Rust / cargo 1.95.0 (MSVC toolchain)
- Tauri CLI 2 — `npm run dist` (= `tauri build`); see [`configurator/BUILD.md`](../../BUILD.md)
- `bundle.targets: "all"` → MSI (WiX) + NSIS setup

## Caveats

- **Unsigned.** Windows SmartScreen shows an "unknown publisher" warning on
  install. Expected for a 0.x pre-release; code signing is a future enhancement.
- **Software-verified only.** The app builds, typechecks (`tsc`), and passes 64
  unit tests; it has **not** been validated against a real Kodi box / OPPO / TV,
  nor installed/launched on a clean Windows machine by the maintainers — that is
  the operator's Phase C below.

## Phase C — operator end-to-end (clean Windows host)

1. Download the MSI (or NSIS `-setup.exe`) from the `configurator-v0.1.0`
   pre-release; confirm its SHA-256 matches the table above.
2. Run the installer. Confirm the SmartScreen "unknown publisher" prompt is the
   only warning and that it installs without error.
3. Launch the app; confirm the window opens (custom frameless title bar,
   1180×820) and the configurator UI renders.
4. Confirm the Start-menu / taskbar icon shows the add-on artwork.
5. Uninstall via Apps & features (or the MSI); confirm clean removal.
