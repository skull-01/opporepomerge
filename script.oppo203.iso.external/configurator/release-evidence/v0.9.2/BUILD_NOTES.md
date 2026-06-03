# Configurator v0.9.2 — build notes

**Released:** 2026-06-03 · **tag:** `configurator-v0.9.2` · **commit:** `07a3f3f`
**Built + published by:** GitHub Actions (`.github/workflows/configurator-ci.yml` → `release` job) on the tag push.
**Bundles add-on:** v2.9.15.

## What shipped — Developer Options UX refinements (umbrella #314)

Operator feedback after the AutoScript ship:

- **PR 1** (#318) — **side-by-side live transcript**: new responsive `.dev-split` layout (controls left, transcript in a tall sticky right column, 1-column under 900px) on the OPPO/TV/AVR/NAS/AutoScript panels.
- **PR 2** (#319) — **Browse + add-on validation** on the Kodi upload: native file picker (`pick_addon_zip` via `rfd`) + `validate_addon_zip` → `{valid, version, reason}` (identity + structure; pure `validate_addon_contents` cargo-tested). Upload + register disabled until a valid OppoKodiAddon zip is picked. Identity check, not cryptographic (unsigned posture).
- **PR 3** (#320) — **TV HDMI input switch**: an "HDMI input switching" card (Switch to OPPO / Switch to Kodi via `planSwitch`, the configured handoff) + ADB HDMI presets.
- **bump** (#321) — 0.9.1 → 0.9.2.

New configurator Rust commands: `validate_addon_zip`, `pick_addon_zip`. New dependency: `rfd` (native file dialog).

## Gates (software-verified only)

- `tsc -b` clean · **vitest 356** · **`cargo test` 53** · `vite build` clean — green on every PR and the tag's CI gate.
- Browser-verified: the 2-column layout (OPPO + TV), the Upload-disabled-until-valid gate, the configured HDMI switch wiring.
- **Hardware validation NOT claimed.** The add-on upload, the native picker + real-zip validation, and the TV HDMI switch against real hardware are **Phase-C** — see [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](../../../docs/MANUAL_VERIFICATION_CHECKLIST.md).

## Artifacts + SHA-256

MSI + NSIS installers + `SHA256SUMS.txt` produced by the CI release job, attached to the published
release (**unsigned**). Verify against that file:

- https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.9.2
