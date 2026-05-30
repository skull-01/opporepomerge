# Configurator v0.4.0 â€” AV receiver database + optional receiver step

**Built:** 2026-05-30 Â· **Source:** `main` (Tauri 2 + React/TS configurator) Â·
**Status:** software-verified only; **unsigned**; no hardware validation.

The fourth Windows binary of the OppoKodiAddon Configurator, distributed as the
GitHub release tagged `configurator-v0.4.0`. It ships one enhancement:

- **AV receiver database + optional Step 5.** A new canonical `avr-models.json`
  adds **224 AV receiver / processor model families (2018â€“2025)** across 10 brands
  (Denon, Marantz, Yamaha, Onkyo, Pioneer, Integra, Sony, Anthem, Arcam, NAD) and
  the US/UK/EU/Asia regions, in the same pattern as the TV database (schema v2,
  lineups + models + region schema). `avrdb.ts` loads it the way `tvdb.ts` loads
  the TV DB â€” per-model/lineup backend resolution, region-first filtering, and a
  remote "Update list" refresh. A new **optional Step 5 (AV Receiver)** surfaces it:
  ask â†’ brand â†’ region/year-filtered model list, showing the candidate control
  backend (Denon/Marantz IP, Yamaha YXC, Onkyo/Pioneer/Integra eISCP, Sony Audio
  API). The step is fully skippable and off the critical path â€” receiver
  automation is off by default in the add-on.

UI/data + loader only â€” no add-on runtime, mapping/generate, or `settings.xml`
changes. Like the TV DB, the AVR DB is not loaded by the add-on at runtime, so
there is **no add-on release** in this cycle.

The binaries are not committed (`target/` is git-ignored); this file records
their identity so the release artifacts are verifiable.

## Artifacts

| Artifact | Size | SHA-256 |
|---|---|---|
| `OppoKodiAddon Configurator_0.4.0_x64_en-US.msi` (MSI) | 3,174,400 B | `338349c4962e781e16458c2de5a7182e71b7e67ff97eb7fc4d5e6e7f37210b90` |
| `OppoKodiAddon Configurator_0.4.0_x64-setup.exe` (NSIS) | 2,067,124 B | `af319ac306b62ba0b95e5fa92a7e0498c4f7c1b8d93becd0e0c5dced14c45ce2` |

Verify after download (PowerShell): `Get-FileHash <file> -Algorithm SHA256`.

## Build environment

- Windows 11 (x64)
- Node v24.15.0 / npm 11.12.1
- Rust / cargo 1.95.0 (MSVC toolchain)
- Tauri CLI 2 â€” `npm run dist` (= `tauri build`); see [`configurator/BUILD.md`](../../BUILD.md)
- `bundle.targets: "all"` â†’ MSI (WiX) + NSIS setup

## Caveats

- **Unsigned.** Windows SmartScreen shows an "unknown publisher" warning on
  install. Expected for a 0.x release; code signing is a future enhancement.
- **Software-verified only.** The app builds, typechecks (`tsc`), and passes 92
  unit tests (18 new for the AVR DB); Step 5 was exercised in a browser preview
  (ask â†’ brand â†’ region-filtered model list render). It has **not** been validated
  against a real Kodi box / OPPO / TV / receiver, nor installed/launched on a
  clean Windows machine by the maintainers â€” that is the operator's Phase C below.
- **Candidate research mapping.** All 224 AVR rows are `validated: false` â€”
  researched candidate mappings, not hardware-validated. Exact regional suffixes,
  tuner variants, and IP/network-control coverage must be confirmed at setup; most
  receivers need Network Standby / IP Control enabled for reliable control.

## Phase C â€” operator end-to-end (clean Windows host)

1. Download the MSI (or NSIS `-setup.exe`) from the `configurator-v0.4.0`
   release; confirm its SHA-256 matches the table above.
2. Run the installer. Confirm the SmartScreen "unknown publisher" prompt is the
   only warning and that it installs without error.
3. Launch the app; confirm the window opens and the configurator UI renders, and
   that the stepper now shows **5 Â· AV Receiver** before the Playback Test.
4. **Step 5 (AV Receiver):** choose "Yes â€” pick my receiver", pick a brand, and
   confirm the Region selector (US/UK/EU/Asia) filters the model list and that each
   row shows platform / candidate backend / regions / receiver type. Confirm the
   "No receiver â€” skip" path jumps straight to the test.
5. Uninstall via Apps & features (or the MSI); confirm clean removal.
