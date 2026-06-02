# Configurator v0.8.1 — audit-remediation fixes + TV DB expansion (bundles add-on 2.9.15)

**Built:** 2026-06-02 · **Source:** `main`@`4621c67` (Tauri 2 + React/TS configurator) ·
**Status:** software-verified only; **unsigned**; no hardware validation.

The Windows binary of the OppoKodiAddon Configurator, distributed as the GitHub release
tagged `configurator-v0.8.1` (holds the repo "Latest"). It bundles the add-on (v2.9.15
code with the 2026-06-02 audit-remediation fixes) and ships:

- **Configurator-side audit fixes** — debug-log secret masking (Sony PSK / SmartThings
  token / AVR PSK inside the generated `settings.xml` blob), single-owner live monitor,
  SSH/HTTP I/O timeouts + deploy rollback, wizard step-number/label corrections, controlled
  Player-IP input, dead/decorative UI cleanup.
- **TV database +110 TCL/Hisense rows (2018–2026)** across CN/US/UK/EU/Asia, 9 existing rows
  updated; total 350→460; all `validated:false` (candidate mappings).
- **Bundled add-on fixes** — AVR http_handoff eligibility, OPPO HTTP path translation +
  launch-failure honesty, SVM3 monitor truth, settings-schema keys, distinct Samsung HDMI
  defaults.

The binaries are not committed (`target/` is git-ignored); this file records their identity
so the release artifacts are verifiable.

## Artifacts

| Artifact | Size | SHA-256 |
|---|---|---|
| `OppoKodiAddon Configurator_0.8.1_x64_en-US.msi` (MSI) | 3,674,112 B | `6fe15a935710bb20a0a965af658b721be45ea9bbde4521f99ea619060113987d` |
| `OppoKodiAddon Configurator_0.8.1_x64-setup.exe` (NSIS) | 2,535,740 B | `69bb36157630ea467e77f109298c4a44ec3b223bee89b168be4083b38647bc9b` |

Bundled add-on: **v2.9.15** (verified inside `src-tauri/resources/addon/script.oppo203.iso.external.zip`).
Verify after download (PowerShell): `Get-FileHash <file> -Algorithm SHA256`.

## Build environment

- Windows 11 (x64)
- Node 20+ / npm 10+
- Rust / cargo (MSVC toolchain)
- Tauri CLI 2 — `npm run dist` (= `bundle:addon` + `tauri build`); see [`configurator/BUILD.md`](../../BUILD.md)
- `bundle.targets` → MSI (WiX) + NSIS setup

## Software gates (this build)

- `tsc --noEmit` 0 · **297 vitest** (incl. `version.test.ts` 3-file version pin + the
  `tv_db_consistency` two-copy guard) · `cargo check` 0 · `vite build` OK.

## Caveats

- **Unsigned.** Windows SmartScreen shows an "unknown publisher" warning on install.
- **Software-verified only.** Not validated against a real Kodi box / OPPO / TV, nor
  installed on a clean Windows machine by the maintainers — operator Phase C below.
- **Candidate research mapping.** The +110 TV rows and the bundled add-on fixes are
  `validated:false` / not hardware-validated.

## Phase C — operator end-to-end (clean Windows host)

1. Download the MSI (or NSIS `-setup.exe`) from the `configurator-v0.8.1` release; confirm
   its SHA-256 matches the table above.
2. Run the installer; confirm SmartScreen "unknown publisher" is the only warning and it
   installs cleanly. Launch; confirm the UI renders.
3. **TV step:** pick a TCL or Hisense brand; confirm the new 2024–2026 model families appear
   under the right region filter with a sane recommended backend.
4. **Debug panel (Ctrl+Shift+D):** run an Apply with a Sony PSK / SmartThings token set;
   confirm the secret is masked in the logged settings.xml blob.
5. Confirm the bundled add-on (v2.9.15 + audit fixes) installs to Kodi and the AVR / Pure-HTTP
   behaviors work on real hardware (per `docs/MANUAL_VERIFICATION_CHECKLIST.md`).
6. Uninstall via Apps & features (or the MSI); confirm clean removal.
