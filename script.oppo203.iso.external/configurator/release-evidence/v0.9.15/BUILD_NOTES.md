# Configurator v0.9.15 — Build Notes

**Theme:** Dev Options → Kodi tab now **accepts the v2 OppoKodiBridge add-on** as well as v1.

**Bundled add-on:** v2.9.17 (unchanged). **Hardware validation:** software-verified only; not
performed / not claimed.

## What changed (PR #368, merge `a289020`)

The dev Kodi tab's add-on handling was hardcoded to `script.oppo203.iso.external`. It now also
recognises the v2 **OppoKodiBridge** service add-on (`service.oppokodibridge`):

- **Validate** — the add-on id is detected from the zip's top-level folder against an accepted-id
  set; the entry-point check is relaxed to `default.py` **or** `service.py` (the v2 add-on is
  service-only), so the v2 zip validates and Upload enables.
- **Upload + Register** — installs to the zip's real id folder (`addons/service.oppokodibridge/`)
  and enables that id; `kodi_set_addon_enabled` validates the id against the accepted set.
- **Version panel** — detects whichever of the two add-ons is installed and shows its id.

Box operations remain hardware-pending; this is a software-only change to the dev tooling.

## Gate (software-verified)

- `npx tsc --noEmit` — clean
- `npx vitest run` — **361 passed**
- `cargo test` — **58 passed** (adds `validate_addon_contents_accepts_oppokodibridge_v2`)
- `npm run dist` (MSI + NSIS) — built for this release

## Artifacts

- `Kodi Oppo External Player Configurator_0.9.15_x64_en-US.msi`
- `Kodi Oppo External Player Configurator_0.9.15_x64-setup.exe` (NSIS)
- `SHA256SUMS.txt`

Published via `scripts/release-configurator-local.ps1` as `configurator-v0.9.15` (repo Latest).
