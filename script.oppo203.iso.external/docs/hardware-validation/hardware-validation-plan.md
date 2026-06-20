# Hardware Validation Plan

## Status

Current status: real hardware validation not performed / not claimed.

The add-on is software-verified, but software tests do not prove behavior on OPPO, Chinoppo, Magnetar, Reavon, TVs, AVRs, or NAS environments.

## Validation principle

Each hardware claim must be tied to a real test report with enough detail for another tester to reproduce the result.

## Required report fields

For every hardware test, capture:

- add-on version
- runtime ZIP filename
- Kodi version
- Kodi platform and OS
- player/device model
- firmware version
- connection method
- media type tested
- network path type
- TV model if TV control is used
- AVR model if AVR sequencing is used
- exact settings used
- pass/fail result
- logs or diagnostic summary
- tester notes

## Test groups

### Core Kodi install

- Install runtime ZIP.
- Confirm add-on appears in Kodi.
- Open settings.
- Run setup wizard.
- Confirm no startup errors.

### OPPO/external handoff

- Test eligible 4K UHD ISO.
- Test eligible UHD disc folder.
- Test non-eligible regular file.
- Confirm non-eligible files are not forced into OPPO path.

### NAS/AutoScript

- Test SMB/NFS path mapping.
- Confirm OPPO-compatible path output.
- Confirm failure messages are actionable.

### TV control

- Test only when configured.
- Confirm failure does not block playback.
- Confirm restore behavior when enabled.

### AVR sequencing

- Confirm disabled AVR path is a no-op.
- Confirm sequencing only runs for eligible handoff.
- Confirm AVR failure does not block playback.
- Confirm restore only runs when enabled.

## Evidence rule

Do not update the project status from `not_performed_not_claimed` until real test reports exist.
