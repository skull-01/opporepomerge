# Build Notes — v2.9.10 Build 8

```yaml
build_id: v2.9.10 Build 8
baseline: script.oppo203.iso.external-2.9.10-build7-dev-source.zip
package: script.oppo203.iso.external-2.9.10-build8.zip
scope: Command TV preset polish
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Purpose

Build 8 improves software-only command/custom TV preset metadata for LG, Samsung, Panasonic, Vizio, and generic command users without adding risky native TV protocol expansion.

## Implementation

- Added explicit command/custom preset IDs: `lg_webos_command`, `samsung_command`, `panasonic_custom_command`, `vizio_custom_command`, and `generic_custom_command`.
- Preserved compatibility presets for existing LG and Samsung command paths.
- Kept presets editable and software-only.
- Preserved `{tv_ip}` placeholder behavior for command templates.
- Marked missing command values as validation-warning conditions.
- Explicitly recorded that no native TV protocols were added.

## Behavior changed

No OPPO playback routing, service interception, `playercorefactory.xml` behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, Roku ECP behavior, Android / Google TV ADB preset metadata, TV-switching non-fatal behavior, or AVR sequencing changed.

## Behavior preserved

- Existing TV backend registry APIs.
- Roku ECP backend behavior.
- Android / Google TV ADB preset metadata.
- ADB command editability.
- Command/custom TV command editability.
- Non-fatal TV switching behavior.
- OPPO playback routing.
- Service interception.
- `playercorefactory.xml` behavior.
- NAS / AutoScript behavior.
- OPPO command-map payloads.
- Startup auto-power behavior.
- AVR sequencing.
- Runtime ZIP policy.
- 99% coverage gate.
- No hardware-validation claim.

## Known limitations

Command/custom TV presets are software-only until real device testing is supplied. They remain user-owned command templates and do not prove LG, Samsung, Panasonic, Vizio, or generic hardware behavior.
