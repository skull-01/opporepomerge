# Build Notes — v2.9.10 Build 5

```yaml
build_id: v2.9.10 Build 5
baseline: script.oppo203.iso.external-2.9.10-build4-dev-source.zip
package: script.oppo203.iso.external-2.9.10-build5.zip
scope: TV backend registry and preset foundation
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Purpose

Build 5 starts the TV expansion phase by introducing side-effect-free TV backend and preset registries. It preserves the existing public `switch_to_oppo(settings)` and `switch_to_kodi(settings)` APIs and the existing backend identifiers `adb`, `sony_bravia`, `lg_command`, `samsung_command`, and `custom_command`.

## Behavior changed

No OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, TV switching execution semantics, or AVR sequencing changed.

## Behavior preserved

- 76-key OPPO command map.
- Stock OPPO wake passthrough.
- Clone-safe wake rewrite.
- Reavon warning-only behavior.
- Magnetar warning-only behavior unless hardware-proven.
- Existing TV switching non-fatal behavior.
- Runtime ZIP exclusion policy.
- 99% coverage gate.

## Known limitations

The Build 5 preset registry is software metadata only. Android TV preset pack, Roku ECP, command-preset polish, SmartThings, diagnostics, and AVR features remain future builds. No real hardware validation is claimed.
