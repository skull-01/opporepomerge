# Build Notes — v2.9.1 Build 6

## Scope

Build 6 adds portable local build/release automation scripts while preserving runtime behavior.

## Changes

- Added `scripts/verify.sh` to run the standard source verification sequence.
- Added `scripts/package_release.sh` to run version consistency checks, create the runtime installable ZIP, generate a SHA256 checksum, and create a dev-source snapshot.
- Added Build 6 regression tests for script syntax, command coverage, packaging output, audit evidence, and runtime ZIP exclusion.
- Added `release-evidence/v2.9.1-build6/MANIFEST.txt` for manifest-based audit evidence.
- Updated `addon.xml`, README, reference, web-references, and release evidence.

## Runtime behavior

No playback, OPPO command-map, service interception, XML routing, NAS playback, startup auto-power, or hardware-control behavior changed.

## Hardware validation

No real OPPO, Chinoppo/M9702/M920x, Kodi, NAS, TV, or ADB hardware validation was performed or claimed.
