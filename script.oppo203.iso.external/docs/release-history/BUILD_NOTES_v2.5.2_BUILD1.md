# Build Notes — v2.5.2 Build 1

## Purpose

v2.5.2 Build 1 starts the OPPO/Chinoppo NAS-mounted playback enhancement line from the v2.5.1 startup-power baseline.

This build is intentionally narrow. It adds family-level capability gates and firmware rules only. It does not add path mapping, AutoScript generation profile changes, playback trigger automation, firmware flashing, or device-side script deployment.

## Planned success rate

90%.

The scope is high confidence because it is limited to pure helpers, tests, documentation, release evidence, and preservation of the v2.5.1 startup-power fix.

## Implemented changes

- Added OPPO UDP-203/UDP-205 jailbroken NAS playback capability gates.
- Added original OPPO 20x AutoScript firmware rules:
  - minimum AutoScript-capable firmware: `20X-56`
  - recommended jailbreak target: `20X-65-0131`
  - unsupported for AutoScript workflows: `20X-54-1127` and older/pre-56 firmware
- Added Chinoppo-family NAS playback capability gates for M9201, M9203, M9205C, M9702, IPUK-UHD8592, GIEC-BDP-G5300, and Magnetar-UDP800 style profiles.
- Recorded the user-provided hardware finding that NAS-mounted file playback on OPPO/Chinoppo-compatible hardware works.
- Preserved the v2.5.1 Build 8 startup-power fix: query `#QPW` before wake, use `#PON` for stock/safe fallback models, use `#EJT` for Chinoppo/clone-family models, and never import the missing `send_token` helper.

## Not implemented in this build

- No path-mapping helper.
- No NAS playback trigger adapter.
- No wizard setup flow for OPPO/Chinoppo NAS playback.
- No AutoScript NFS profile generation changes.
- No device-side script push or firmware modification.
- No claim of universal hardware validation.

## Files changed

- `addon.xml`
- `service.py`
- `resources/lib/settings_reader.py`
- `tests/test_v252_build1_nas_capability.py`
- `tools/audit_release.py`
- release evidence and hardware-validation tracker files for v2.5.2 Build 1
