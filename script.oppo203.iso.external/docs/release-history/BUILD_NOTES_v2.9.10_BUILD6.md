# Build Notes — v2.9.10 Build 6

```yaml
build_id: v2.9.10 Build 6
baseline: script.oppo203.iso.external-2.9.10-build5-dev-source.zip
package: script.oppo203.iso.external-2.9.10-build6.zip
scope: Android / Google TV preset pack
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Purpose

Build 6 extends the Build 5 TV preset registry with editable Android / Google TV ADB software presets for TCL, Sony, Hisense, Philips, Xiaomi, Sharp, Skyworth/Coocaa, Haier, and generic Android TV / Google TV.

## Behavior changed

No OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, TV switching execution semantics, or AVR sequencing changed.

## Behavior preserved

- Existing TV backend registry APIs.
- Existing public `switch_to_oppo(settings)` and `switch_to_kodi(settings)` APIs.
- Existing ADB command editability through `oppo_input_adb_shell` and `kodi_input_adb_shell`.
- Existing non-fatal TV switching behavior.
- 76-key OPPO command map.
- Stock OPPO wake passthrough.
- Clone-safe wake rewrite.
- Reavon and Magnetar warning-only posture unless hardware-proven.
- Runtime ZIP exclusion policy.
- 99% coverage gate.

## Known limitations

The Build 6 Android / Google TV presets are software metadata only. No universal ADB HDMI command is claimed. Hardware validation is not claimed and remains tester-owned per model.
