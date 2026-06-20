# Configurator v0.9.7 — build notes

**Released:** 2026-06-04 · **tag:** `configurator-v0.9.7`
**Built + published by:** GitHub Actions (`.github/workflows/configurator-ci.yml` → `release` job) on the tag push.
**Bundles add-on:** v2.9.17 — the CI `bundle:addon` step repackages `main`'s add-on source (now carrying the player-DB enrichment) into the installer.

## What shipped

Pairs the configurator with the **add-on v2.9.17** release (player-DB enrichment: five OPPO-clone variants — M9205 V2/V3/V4, M9702 Plus, VenPro V203 — plus a cross-area Dolby Vision data layer). The configurator's Step-2 player picker and `oppo_hardware_model` mapping surface the five new models automatically from the bundled players DB; **no configurator UI code changed** (the picker is derived from `players-models.json`).

### Release-title branding fix
The `configurator-ci.yml` release job now titles the GitHub release **"Kodi Oppo External Player Configurator v\<version\>"** (derived from the tag), replacing the stale generic `"Configurator \<tag\>"` that had lagged the v0.9.6 rebrand. `configurator-v0.9.6` was retitled to match.

### Version bump → tag `configurator-v0.9.7`
`package.json` / `tauri.conf.json` / `Cargo.toml` / `Cargo.lock` bumped 0.9.6 → 0.9.7 (pinned by `version.test.ts`).

## Gates (software-verified only)

- Configurator: `tsc -b` clean · **vitest 361** (incl. `version.test.ts` 3-file consistency on 0.9.7) · `cargo test` (PR gate) · `vite build`.
- The installer logic (vendored `installer.nsi` / `installer-hooks.nsh`) is **unchanged from v0.9.6**, which compiled cleanly; the version bump flows into the MSI/NSIS artifact filenames only. The MSI/NSIS installers are built + published by the CI release tag job (watched to completion).
- **Hardware validation NOT claimed.** Operator / Phase-C: on a real Windows host, confirm the v0.9.7 installer shows the **Kodi Oppo External Player Configurator** brand, an upgrade from v0.9.6 behaves, and the bundled add-on reports **v2.9.17** (the new clone models appear in the Step-2 picker). See [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](../../../docs/MANUAL_VERIFICATION_CHECKLIST.md).

## Artifacts + SHA-256

MSI + NSIS installers + `SHA256SUMS.txt` produced by the CI release job, attached to the published release (**unsigned** — Windows SmartScreen shows an "unknown publisher" warning; expected). Verify against that file:

- https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.9.7
