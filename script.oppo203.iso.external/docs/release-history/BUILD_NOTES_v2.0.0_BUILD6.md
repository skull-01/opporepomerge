# Build Notes — Version 2.0.0 Build 6

```yaml
addon_version: 2.0.0.6
artifact_name: script.oppo203.iso.external-2.0.0-build6.zip
checksum_name: script.oppo203.iso.external-2.0.0-build6.sha256
baseline: script.oppo203.iso.external-2.0.0.zip / package version 2.0.0
build_type: build-id update / stability-preserving repackaging
scope: no runtime feature expansion
```

## Summary

Build 6 changes the package/build identity from final `2.0.0` to build-id version `2.0.0.6` at the user's request. The change is intentionally narrow and preserves the v2.0 MVP behavior already verified in the final package.

## Changes

- Updated `addon.xml` version to `2.0.0.6`.
- Updated release-audit expectations and tests to verify `2.0.0.6`.
- Added this Build 6 notes file.
- Added `RELEASE_MANIFEST_v2.0.0_BUILD6.md`.
- Updated `README.md`, `reference.md`, and `web-references.md` with Build 6 sections.
- Kept final `RELEASE_NOTES_v2.0.0.md`, `RELEASE_MANIFEST_v2.0.0.md`, `MVP_COMPLIANCE_MATRIX_v2.0.0.md`, and `HARDWARE_VALIDATION_v2.0.0.md` in the package for release-history continuity.

## Behavior preserved

- External Player MVP flow.
- M9702 / Chinoppo `#PON` and `#POW` rewrite to `#EJT`.
- Stock OPPO power-command pass-through.
- TCL / Android TV ADB switching remains optional and failure-safe.
- Session sentinel cleanup behavior.
- Fake OPPO server tests.
- Kodi stub import tests.
- Command map remains canonical at 76 keys with no `#SIS`, `#PGU`, or `#PGD`.

## Known caveats

No physical OPPO, M9702/Chinoppo, TCL/Android TV, Kodi installation, or ADB hardware test was performed for this build-id update. Hardware validation remains documented from prior project/user evidence only.
