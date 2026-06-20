# Configurator v0.8.3 — installer old-version check (bundles add-on 2.9.15)

**Built:** 2026-06-03 · **Source:** `main`@`62912e2` (Tauri 2 + React/TS configurator) ·
**Status:** software-verified only; **unsigned**; no hardware validation.

The Windows binary of the OppoKodiAddon Configurator, distributed as the GitHub release tagged
`configurator-v0.8.3` (holds the repo "Latest"). It adds an installer-side old-version check and
bundles the add-on (v2.9.15).

- **Installer old-version check (PR #262).** A new NSIS `NSIS_HOOK_PREINSTALL`
  (`configurator/src-tauri/installer-hooks.nsh`, wired via `bundle.windows.nsis.installerHooks`):
  on install, detect any previously-installed version of the configurator — our own NSIS install
  (the uninstall key) **and** any MSI install of the same product in the per-machine uninstall
  registry — and offer, in one Yes/No prompt, to **remove all old versions** before installing,
  then proceed. Complements Tauri's built-in reinstall page (which already offers to remove the
  primary detected install) by also clearing a parallel MSI install on opt-in. The MSI installer
  continues its automatic in-place WiX upgrade.

The binaries are not committed (`target/` is git-ignored); this file records their identity.

## Artifacts

| Artifact | Size | SHA-256 |
|---|---|---|
| `OppoKodiAddon Configurator_0.8.3_x64_en-US.msi` (MSI) | 3,682,304 B | `41f6b0e593eb68fe56fa2e7454e28fe3cf68d609e89c46f92c60c63fa8e72242` |
| `OppoKodiAddon Configurator_0.8.3_x64-setup.exe` (NSIS) | 2,540,337 B | `7655161dcf41c1486ca52517edd80e0cf7845d89708b44326173f4d519706e52` |

Bundled add-on: **v2.9.15** (verified inside `src-tauri/resources/addon/script.oppo203.iso.external.zip`).

## Build environment

- Windows 11 (x64); Node 20+ / npm 10+; Rust / cargo (MSVC); Tauri CLI 2 — `npm run dist`.

## Software gates (this build)

- `tsc --noEmit` 0 · **301 vitest** · `cargo check` 0 · `npm run dist` OK — **`makensis` compiled
  the hook into the installer** (the generated `target/release/nsis/x64/installer.nsi` carries
  `!include "...installer-hooks.nsh"` + `!insertmacro NSIS_HOOK_PREINSTALL`).

## Caveats

- **Unsigned**; **software-verified only**. The installer's detect/remove **runtime behaviour is
  NOT hardware-validated** — only that the hook compiles into the installer.

## Phase C — operator end-to-end (clean Windows host)

1. Install v0.8.2 (or earlier) first, then run the **v0.8.3 NSIS setup**; confirm the "Remove all
   old versions before installing?" prompt appears and, on **Yes**, the old version is uninstalled
   before v0.8.3 installs; on **No**, the install proceeds without removing it.
2. Repeat with an **MSI** install present; confirm it is offered for removal too.
3. With **no** prior install, confirm the prompt does **not** appear and the install proceeds.
4. Verify SHA-256 of the downloaded artifacts against the table above.
