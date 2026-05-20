# v2.9.10 Build 9A — SmartThings experimental settings and acknowledgement skeleton

Build 9A implements the safe first half of the SmartThings roadmap item. It adds SmartThings as an explicitly experimental, metadata-only TV layer.

## Scope

- Added `smartthings` backend metadata with live API calls disabled.
- Added SmartThings experimental preset metadata.
- Added settings placeholders for acknowledgement, token, device ID, and input IDs.
- Added token-redaction and validation metadata helpers in `resources/lib/smartthings_control.py`.
- Added tests for acknowledgement gating, redaction, metadata, and refusal to execute live SmartThings calls.

## Preserved behavior

No OPPO playback routing, service interception, `playercorefactory.xml`, NAS/AutoScript, OPPO command map, startup auto-power, Roku ECP, Android TV ADB presets, command/custom TV presets, AVR sequencing, runtime ZIP policy, or hardware-validation behavior changed.

## Hardware status

Hardware validation was not performed and is not claimed.
