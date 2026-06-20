# Configurator v0.8.7 — hidden Step 0 "Not yet" + TV family sizes + E8N Pro (bundles add-on 2.9.15)

**Built:** 2026-06-03 · **Source:** `main`@`4424441` (tag `configurator-v0.8.7`) ·
**Status:** software-verified only; **unsigned**; no hardware validation.

Built and published by CI (the `configurator-v0.8.7` tag → `.github/workflows/configurator-ci.yml`
gate → release job → `npm run dist` → publish as Latest). Ships the post-v0.8.6 changes:

- **Hidden Step 0 "Not yet" button (PR #281)** — the OPPO NAS-access setup path (`step0_exit`) is
  hidden for now (unsupported); the screen + routing stay registered (dormant) so it's a one-button
  restore later.
- **TV-step family screen sizes (PR #282)** — an optional `sizes` array on a TV model family is
  rendered as a "Sizes: 65″ · 75″ · 85″ · 100″" line for user reassurance, plus a universal note that
  TVs are listed by family and every size shares the same control setup. Size never affects backend
  selection. Seeded the Hisense E8N Pro.
- **Hisense E8N Pro in the TV DB (PR #280)** — China, 2024, ULED X Mini LED, under a new
  `hisense-china-android` lineup (Android/JUUI, not VIDAA/Google TV); `custom_command` primary +
  `adb` fallback; `validated:false`. Bundled here as the offline fallback (it was already live to
  installed apps via the in-app "Update database" button on `main`'s docs copy).

The binaries are not committed (`target/` is git-ignored); this file records their identity.

## Artifacts

| Artifact | Size | SHA-256 |
|---|---|---|
| `OppoKodiAddon Configurator_0.8.7_x64_en-US.msi` (MSI) | 3,694,592 B | `13f72bcf29754060fd4a5cd4652c6f2c98a4db161ce75541fc8d4bbbcfccd8f0` |
| `OppoKodiAddon Configurator_0.8.7_x64-setup.exe` (NSIS) | 2,556,655 B | `a8e65f581999d2c4dcebe1d578f3936aedba6bfad52fd791e2e65474f7157580` |

A `SHA256SUMS.txt` is attached to the release. Bundled add-on: **v2.9.15**.

## Build environment

- GitHub Actions `windows-latest`; Node 20; Python 3.12; Rust stable (MSVC); Tauri CLI 2 — via
  `.github/workflows/configurator-ci.yml`.

## Software gates (this release)

- Gate job green: `tsc -b` + `vite build` + vitest + `cargo test` (after `bundle:addon`). vitest 321;
  TV DB consistency guard + tvdb size-field tests green.
- Browser-verified the hidden "Not yet" button and the E8N Pro "Sizes: 65″ · 75″ · 85″ · 100″" line.

## Caveats

- **Unsigned**; **software-verified only.** Installer runtime, on-box paths, and device control are
  operator (Phase C).

## Phase C — operator end-to-end (real Windows host)

1. Install the published MSI/NSIS; verify SHA-256 against the table above.
2. Confirm Step 0 shows only "I can already play ISOs on my player" + "Reset all configurations…".
3. In the TV step (Hisense / CN), confirm the E8N Pro lists "Sizes: 65″ · 75″ · 85″ · 100″".
