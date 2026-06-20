# Build Notes — v2.9.1 Build 2

```yaml
build: v2.9.1 Build 2
baseline: script.oppo203.iso.external-2.9.1-build1-dev-source.zip
scope: centralized disc classification and safe shared constants
planned_success_rate: 88 percent
runtime_behavior_changed: false
hardware_validation_claimed: false
```

## Summary

Build 2 begins the clean-code roadmap by centralizing duplicated 4K/UHD/2160p disc-style classification constants and helpers.

## Changes

- Added `resources/lib/disc_classification.py`.
- Added `resources/lib/constants.py`.
- Updated `resources/lib/intercept.py` to delegate its 4K disc-source wrappers to the shared classifier while preserving its public API.
- Updated `resources/lib/installer.py` and `resources/lib/playercorefactory_merge.py` to import the same Option 4 XML pattern and filetype constants.
- Updated `tools/audit_release.py` to read the 76-key and 99% protected constants where safe.
- Added `tests/test_v291_build2_disc_classification.py`.

## Behavior preserved

- Tagged 4K/UHD/2160p ISO and BDMV navigation/playlist sources remain candidates.
- Untagged disc-style sources remain rejected by the 4K service classifier.
- Loose/raw video files such as MKV, MP4, M2TS, TS, and VOB remain with Kodi.
- Option 4 XML still routes only `iso`, `bdmv`, and `mpls` with a 4K/UHD/2160p filename/path tag.
- OPPO command maps, startup auto-power, NAS adapter, and hardware-control behavior were not changed.

## Hardware status

No hardware validation was performed or claimed.
