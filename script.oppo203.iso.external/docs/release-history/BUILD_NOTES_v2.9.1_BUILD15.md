# BUILD NOTES — v2.9.1 Build 15

## Build identity

```yaml
addon_version: 2.9.1
build_id: v2.9.1 Build 15
baseline: script.oppo203.iso.external-2.9.1-build14-dev-source.zip
scope: Babel/gettext extraction transition with make_pot fallback preserved
runtime_behavior_changed: false
hardware_validation: not_performed_not_claimed
```

## Summary

Build 15 implements the cleanup-roadmap i18n extraction transition. It adds `tools/i18n_extract.py` as a transition-safe extraction facade and `babel.cfg` as a Babel/gettext configuration reference, while preserving `tools/make_pot.py` as the deterministic Kodi numeric-id fallback for this build.

The add-on uses Kodi numeric localization ids stored as gettext `msgctxt` values, so Build 15 does not make Babel a hard dependency and does not rely on Babel to understand every Kodi numeric-id call. The new facade supports a dependency-safe `--backend auto` mode and a non-writing `--check` mode used by verification.

## Files changed or added

- Added `tools/i18n_extract.py`.
- Added `babel.cfg`.
- Added `tests/test_v291_build15_i18n_extraction_transition.py`.
- Added `release-evidence/v2.9.1-build15/MANIFEST.txt`.
- Added Build 15 evidence files.
- Updated `scripts/verify.sh` to compile and check i18n extraction tooling.
- Updated `scripts/package_release.sh` default suffix to `build15`.
- Updated `resources/lib/version.py` to Build 15.
- Updated `addon.xml`, `README.md`, `reference.md`, `web-references.md`, and `docs/sources.yaml`.

## Preserved behavior

No playback, OPPO command-map behavior, service interception policy, XML routing policy, NAS adapter behavior, startup auto-power behavior, settings runtime behavior, audit outcome semantics, packaging outcome semantics, or hardware-control behavior changed.

The installable ZIP remains runtime-only and excludes `tools/`, `scripts/`, `docs/`, tests, release evidence, handoff files, and development-only extraction configuration.
