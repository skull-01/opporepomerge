# Hardware Validation - Version 2.0.0 Build 4

## Status

Manual hardware validation is recorded as **assumed passed** for Build 4 based on the user instruction:

```text
Assume that I have tested the latest build with the real hardware and no issues were found.
```

## Scope recorded

The assumed validation covers the MVP real-hardware path represented by the latest tested build:

| Area | Status | Notes |
|---|---|---|
| OPPO / OPPO-compatible external player flow | Assumed passed | User reported no hardware issues. |
| M9702 / Chinoppo wake behavior | Assumed passed | Build retains clone-only `#PON` / `#POW` to `#EJT` behavior. |
| Stock OPPO power command behavior | Assumed passed | Build retains `#PON` and `#POW` for stock OPPO profiles. |
| TCL / Android TV ADB switching | Assumed passed | Build keeps TV switching optional and non-fatal. |
| Kodi handoff experience | Assumed passed | No issues reported from the real-hardware test. |

## Important limitation

The automated CI/test environment still does not contain the physical OPPO/M9702 player, TCL/Android TV, ADB device, or Kodi runtime. This file records the manual validation result as project input; it is not an automated proof.

## Retest trigger

Manual hardware validation should be repeated after any future build that changes:

- `resources/lib/oppo_control.py`
- `resources/lib/oppo_remote.py`
- `resources/lib/external_player.py`
- `resources/lib/tv_control.py`
- `resources/lib/adb_control.py`
- `resources/settings.xml`
- packaging/installation layout
- Kodi entry points such as `default.py` or `service.py`
