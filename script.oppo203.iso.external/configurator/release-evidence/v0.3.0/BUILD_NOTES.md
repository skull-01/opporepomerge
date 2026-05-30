# Configurator v0.3.0 — TV database schema v2 + region filtering + players DB

**Built:** 2026-05-30 · **Source:** `main` (Tauri 2 + React/TS configurator) ·
**Status:** software-verified only; **unsigned**; no hardware validation.

The third Windows binary of the OppoKodiAddon Configurator, distributed as the
GitHub release tagged `configurator-v0.3.0`. It ships two enhancements:

- **TV database → schema v2 (#103, PR #104).** The TV control-path database grows
  from the 8-row v1 seed to **296 model families (2018–2025)** across Samsung, LG,
  Sony, TCL and Hisense, with per-model region metadata. Step 3 leads with a
  Region selector (US/UK/EU/Asia) and each model row surfaces platform, primary +
  fallback backends, mapped regions, mapping confidence, and a preferred/fallback/
  probe tier chip.
- **Players database (#105, PR #106).** A new canonical `players.json` consolidates
  the OPPO/clone player taxonomy (18 model families + brand display metadata +
  candidate regions) in the same pattern as the TV DB; `players.ts` derives the
  Step 2 catalog from it and the screen surfaces each model's markets, wake
  command, hardware class, and NAS-playback candidacy. A consistency guard test
  pins the JSON to the add-on's live registries.

UI/data + loader only — no add-on runtime, mapping/generate, or `settings.xml`
ordering changes.

The binaries are not committed (`target/` is git-ignored); this file records
their identity so the release artifacts are verifiable.

## Artifacts

| Artifact | Size | SHA-256 |
|---|---|---|
| `OppoKodiAddon Configurator_0.3.0_x64_en-US.msi` (MSI) | 3,166,208 B | `2bb264d9819a497bb610166aee80f7f320fae342bf6973db213aebbc1e811825` |
| `OppoKodiAddon Configurator_0.3.0_x64-setup.exe` (NSIS) | 2,065,049 B | `86229c52b9f4a52f101f8ae28f92962b63d3bf43b91843abacfdbbf6b5498360` |

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
- **Software-verified only.** The app builds, typechecks (`tsc`), and passes 74
  unit tests; it has **not** been validated against a real Kodi box / OPPO / TV,
  nor installed/launched on a clean Windows machine by the maintainers — that is
  the operator's Phase C below.
- **Candidate research mapping.** All 296 TV rows and all player regions are
  `validated: false` — researched candidate mappings, not hardware-validated.
  Exact regional suffixes and SKUs must be confirmed at setup.

## Phase C — operator end-to-end (clean Windows host)

1. Download the MSI (or NSIS `-setup.exe`) from the `configurator-v0.3.0`
   release; confirm its SHA-256 matches the table above.
2. Run the installer. Confirm the SmartScreen "unknown publisher" prompt is the
   only warning and that it installs without error.
3. Launch the app; confirm the window opens and the configurator UI renders.
4. **Step 3 (TV):** pick a brand; confirm the Region selector filters the model
   list (e.g. Hisense US vs Asia shows different models) and that rows show
   platform / backend / regions / confidence and a tier chip.
5. **Step 2 (Player):** pick a brand + model; confirm the facts line shows
   markets, wake command, hardware class, and (for clones) NAS-playback candidate.
6. Uninstall via Apps & features (or the MSI); confirm clean removal.
