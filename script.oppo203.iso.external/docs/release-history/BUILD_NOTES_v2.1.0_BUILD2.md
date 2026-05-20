# Build Notes — v2.1.0 Build 2

```yaml
addon_version: 2.1.0.2
artifact_name: script.oppo203.iso.external-2.1.0-build2.zip
baseline: script.oppo203.iso.external-2.1.0-build1.zip
release_line: post-MVP coverage hardening before full merge
coverage_gate: 94
coverage_target_long_term: 99
real_hardware_validation: not performed; deferred until after full merge
```

## Summary

This build continues the gradual 99% coverage path. It keeps feature scope stable and raises the enforced coverage gate from 92% to 94%.

## Controlled changes

- Added targeted coverage tests for AutoScript generation and wizard paths.
- Added discovery cache save/load and probe exception branch tests.
- Added OPPO remote fallback and hardware-gate exception tests.
- Added external-player idle/trick-play suppression and disabled-TV path tests.
- Added small support-helper tests for logging, playercorefactory merge, and preset-manager edge cases.
- Updated `.coveragerc` to `fail_under = 94`.
- Updated release audit to require at least 94%.

## Non-goals

- No full v1.1.9 + v0.9.14 merge.
- No new runtime feature scope.
- No claim of physical OPPO, TV, ADB, or Kodi hardware validation.
