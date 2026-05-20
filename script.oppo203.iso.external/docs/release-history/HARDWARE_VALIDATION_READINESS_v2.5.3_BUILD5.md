# Hardware Validation Readiness — v2.5.3 Build 5

Build 5 introduces `resources/lib/hardware_validation_readiness.py`, a read-only helper that produces a tester-ready report before physical validation.

## Purpose

The report standardizes what a hardware tester should record, especially for the v2.5.3 4K UHD disc-style interception line.

## Report contents

- Add-on diagnostic summary.
- Setup completeness and warnings.
- Hardware model and NAS/AutoScript capability gate.
- Option 4 XML naming requirements.
- Positive tests for tagged `4K`, `UHD`, or `2160p` disc-style sources.
- Negative tests proving loose/raw video stays with Kodi.
- Required tester result fields.
- Explicit `hardware_validation_claimed: false` posture.

## Explicit caveat

The readiness report does not contact hardware, run playback, perform HDMI switching, or prove OPPO/Chinoppo behavior. It only prepares evidence collection for the user-owned hardware test.
