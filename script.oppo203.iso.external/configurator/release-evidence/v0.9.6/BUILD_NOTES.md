# Configurator v0.9.6 — build notes

**Released:** 2026-06-04 · **tag:** `configurator-v0.9.6`
**Built + published by:** GitHub Actions (`.github/workflows/configurator-ci.yml` → `release` job) on the tag push.
**Bundles add-on:** v2.9.16 — the CI `bundle:addon` step repackages `main`'s add-on source into the installer (unchanged since configurator-v0.9.5).

## What shipped

**Rebrand** — the Windows configurator is renamed from **OppoKodiAddon Configurator** to **Kodi Oppo External Player Configurator**, and the in-app title bar now shows the live version.

### Rebrand to "Kodi Oppo External Player Configurator" — [#338](https://github.com/skull-01/script.oppo203.iso.external/pull/338)

- `productName` + window title (`tauri.conf.json`) — drives the installer display name, Start-Menu shortcut, uninstall entry, and the MSI/NSIS artifact filenames.
- Browser/tab title (`index.html`) and i18n `app.title`.
- In-app `WinShell` title bar now renders `"{name}-v{version}"` → **Kodi Oppo External Player Configurator-v0.9.6**, with the version injected at build time from `package.json` via a Vite `define` (`__APP_VERSION__`), so it tracks each release with no manual edits.
- NSIS preinstall-hook header comment.
- Bundle **identifier unchanged** (`com.script-oppo203-iso-external.configurator`) — preserves NSIS/MSI upgrade detection and `app_data_dir`, so existing user state is not orphaned. The version stays out of `productName`, so the exe / Start-Menu / uninstall-entry names don't churn per release.

### Version bump → tag `configurator-v0.9.6`

`package.json` / `tauri.conf.json` / `Cargo.toml` / `Cargo.lock` bumped 0.9.5 → 0.9.6 (pinned by `version.test.ts`).

## Gates (software-verified only)

- Configurator: `tsc -b` clean · **vitest 359** (incl. `version.test.ts` 3-file consistency) · **`cargo test` 57** · `vite build`.
- **MSI + NSIS compile verified locally** before tagging: `npm run dist` ran WiX (`candle`/`light`) and `makensis` against the renamed `productName` + the vendored `installer.nsi` / `installer-hooks.nsh`, producing:
  - `Kodi Oppo External Player Configurator_0.9.6_x64_en-US.msi`
  - `Kodi Oppo External Player Configurator_0.9.6_x64-setup.exe`
  The configurator PR gate does **not** run `tauri build` — only the release tag job and this local build do — so the rename was confirmed to bundle cleanly before the tag was pushed.
- **Hardware validation NOT claimed.** Operator / Phase-C: on a real Windows host, confirm the installer display name, Start-Menu shortcut, uninstall entry, exe filename, and desktop window title all read the new brand, and that an upgrade from a prior install behaves. Note: the parallel-MSI branch of the preinstall hook matches `DisplayName == ${PRODUCTNAME}`, so the first post-rename installer will not auto-detect an *old-named MSI* install (NSIS upgrade detection is identifier-keyed and unaffected). See [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](../../../docs/MANUAL_VERIFICATION_CHECKLIST.md).

## Artifacts + SHA-256

MSI + NSIS installers + `SHA256SUMS.txt` produced by the CI release job, attached to the published
release (**unsigned** — Windows SmartScreen shows an "unknown publisher" warning; this is expected). Verify against that file:

- https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.9.6
