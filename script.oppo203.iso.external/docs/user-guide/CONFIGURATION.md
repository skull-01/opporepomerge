# Configuration Guide

## Recommended setup order

1. Select the player/profile that best matches the target device.
2. Configure the player address or external-player path settings.
3. Confirm media eligibility and path mapping.
4. Test base handoff with TV and AVR automation disabled.
5. Enable TV switching only after base handoff works.
6. Enable AVR sequencing only after base handoff and TV behavior are stable.
7. Export diagnostics if a setup step fails, then review logs for secrets before sharing.

## Media routing policy

The protected v2.9.10 behavior is conservative. Disc-style media can be routed externally, while ordinary loose/raw video files should remain with Kodi unless the project explicitly changes that policy in a later build.

## TV and AVR behavior

TV and AVR control paths are optional. Failures in these paths should be non-fatal and must not block playback routing.
