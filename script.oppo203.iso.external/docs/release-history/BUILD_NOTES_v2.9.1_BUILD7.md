# Build Notes — v2.9.1 Build 7

## Scope

Build 7 implements the packaging allowlist cleanup from the 16-build roadmap. The runtime installable ZIP is now selected by an explicit allowlist: root runtime files, optional runtime assets, and `resources/**`. Development folders and evidence are excluded by omission rather than by matching long filename-prefix denylists.

## Runtime behavior

No playback, OPPO command, service interception, XML routing, NAS adapter, startup auto-power, or hardware-control behavior changed.

## Files changed

- `tools/package_installable_zip.py`
- `scripts/package_release.sh`
- `resources/lib/version.py`
- `addon.xml`
- `tests/test_v291_build5_version_source.py`
- `tests/test_v291_build6_release_automation.py`
- `tests/test_v291_build7_packaging_allowlist.py`
- release evidence and documentation files

## Hardware validation

No hardware validation was performed or claimed.
