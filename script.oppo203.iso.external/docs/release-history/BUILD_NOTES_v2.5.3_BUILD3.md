# Build Notes — v2.5.3 Build 3

```yaml
build: v2.5.3 Build 3
addon_version: 2.5.3
package: script.oppo203.iso.external-2.5.3-build3.zip
baseline: script.oppo203.iso.external-2.5.3-build2-dev-source.zip
scope: version identity and audit reconciliation
runtime_behavior_change: false
hardware_validation: not_performed
```

## Summary

Build 3 reconciles the runtime `addon.xml` version with the v2.5.3 package/build identity. Build 2 intentionally left `addon.xml` at `2.5.2` because inherited audit tests expected that value. Build 3 removes that mismatch by updating `addon.xml` to `2.5.3`, updating audit/test expectations, and adding Build 3 release evidence.

## Preserved behavior

- v2.5.3 Build 1 precise Python service interception for tagged 4K/UHD/2160p disc-style sources.
- v2.5.3 Build 2 conservative Option 4 `playercorefactory.xml` routing.
- Loose/raw video files remain with Kodi.
- Runtime ZIP remains focused on Kodi runtime files only.
- No OPPO command-map, Reavon, startup-power, NAS playback, or hardware-control behavior changed.

## Files changed

- `addon.xml`
- `tools/audit_release.py`
- current-version test expectations under `tests/`
- `tests/test_v253_build3_version_identity.py`
- `README.md`
- `reference.md`
- `web-references.md`
- Build 3 evidence files

## Hardware status

No real OPPO, Chinoppo/M9702, Kodi installation, NAS, TV, or ADB hardware validation was performed. Hardware validation remains user-owned.
