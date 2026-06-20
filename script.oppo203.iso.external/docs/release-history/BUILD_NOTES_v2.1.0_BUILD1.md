# Build Notes — v2.1.0 Build 1

```yaml
addon_version: 2.1.0.1
baseline: script.oppo203.iso.external-2.0.0.zip
artifact_name: script.oppo203.iso.external-2.1.0-build1.zip
focus: 92 percent coverage gate hardening
release_line: v2.1 post-MVP hardening
```

## Summary

This build addresses the previously deferred 92 percent coverage gate without starting the full v1.1.9 + v0.9.14 superset merge.

## Changes

- Added coverage-focused tests in `tests/test_coverage_hardening.py`.
- Raised `.coveragerc` from `fail_under = 85` to `fail_under = 92`.
- Fixed `resources/lib/installer.py` so the wizard auto-launch fallback path can log through `xbmc.log()` without a missing import.
- Updated `README.md`, `reference.md`, and `web-references.md`.
- Updated `tools/audit_release.py` to check the 92 percent gate configuration and require Build 1 evidence files.

## Safety notes

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested. Runtime feature scope was not expanded.
