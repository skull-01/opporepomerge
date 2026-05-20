# Build Notes — v2.9.10 Build 17

## Scope

Unified TV + AVR playback sequencing for the external-player flow.

## Changes

- Added `resources/lib/avr_sequence.py` as a non-throwing sequencing helper.
- Updated `resources/lib/external_player.py` to run TV switch-to-OPPO, optional AVR pre-playback sequence, OPPO start, OPPO stop, optional AVR restore, and existing TV switch-back in a safe order.
- Updated AVR support metadata to indicate playback sequencing is now hooked.
- Added `tests/test_v2910_build17_unified_playback_sequence.py`.
- Updated active v2.9.10 tests from Build 16 identity to Build 17 identity.

## Preserved behavior

Startup power, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, OPPO command-map payloads, TV failure nonfatal behavior, AVR disabled no-op behavior, runtime ZIP policy, 99% coverage gate, and no-hardware-validation-claim posture remain preserved.
