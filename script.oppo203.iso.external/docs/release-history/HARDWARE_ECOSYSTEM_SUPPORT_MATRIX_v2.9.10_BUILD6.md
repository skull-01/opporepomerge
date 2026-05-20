# Hardware Ecosystem Support Matrix — v2.9.10 Build 6

## Player layer

Stock OPPO, Chinoppo-style clones, experimental clones, and OPPO-like successors retain the Build 5 support posture. Reavon and Magnetar remain warning-only unless hardware-proven.

## TV layer

| Preset | Backend | Build 6 status | Notes |
|---|---|---|---|
| TCL Android TV / Google TV | adb | software preset | Editable ADB command fields; hardware validation required |
| Sony Android TV / Google TV | adb | software preset | Model-specific ADB behavior must be tested |
| Hisense Android TV / Google TV | adb | software preset | Model-specific ADB behavior must be tested |
| Philips Android TV / Google TV | adb | software preset | No universal ADB HDMI command is claimed |
| Xiaomi Android TV / Google TV | adb | software preset | Commands remain editable |
| Sharp Android TV | adb | software preset | Hardware validation required |
| Skyworth / Coocaa Android TV | adb | software preset | Commands remain editable |
| Haier Android TV | adb | software preset | Hardware validation required |
| Generic Android TV / Google TV | adb | software preset | User-owned command template |

Existing Build 5 backends remain preserved: `adb`, `sony_bravia`, `lg_command`, `samsung_command`, and `custom_command`. Preset registry entries are software-only and require real hardware validation before confirmed support is claimed.

## AVR layer

AVR support is not implemented in Build 6. Future v2.9.10 AVR builds remain disabled by default.
