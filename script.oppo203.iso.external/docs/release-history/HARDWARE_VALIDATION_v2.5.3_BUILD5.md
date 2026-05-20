# Hardware Validation Status — v2.5.3 Build 5

No real hardware validation was performed for Build 5.

Build 5 adds readiness/export tooling only. The exported report is a checklist and diagnostic aid; it is not evidence that hardware validation passed.

## Not tested by this build

- Real OPPO UDP-203/UDP-205 hardware.
- Real Chinoppo/M9702/M920x hardware.
- Real Kodi install/runtime behavior.
- Real NAS path visibility from the player.
- Real TCL/Android TV ADB switching.
- Real HDMI input switching.

## Required tester evidence before claiming hardware validation

- Device model and firmware/build.
- Kodi platform and version.
- OPPO IP/port and observed command response.
- Tagged 4K/UHD/2160p ISO/BDMV/MPLS handoff result.
- Loose/raw video negative-test result.
- Option 4 XML behavior if XML mode is used.
- NAS path mapping and player-visible path result.
- TV switching result if enabled.
- Logs and issues for any failure.
