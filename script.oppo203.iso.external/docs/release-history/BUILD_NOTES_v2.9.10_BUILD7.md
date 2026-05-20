# Build Notes — v2.9.10 Build 7

```yaml
build_id: v2.9.10 Build 7
baseline: script.oppo203.iso.external-2.9.10-build6-dev-source.zip
package: script.oppo203.iso.external-2.9.10-build7.zip
scope: Roku TV ECP backend
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Purpose

Build 7 adds a local Roku TV ECP backend for optional TV input switching while preserving the existing OPPO external-player workflow.

## Implementation

- Added `resources/lib/roku_ecp_control.py`.
- Added the `roku_ecp` backend to the TV backend registry.
- Added Roku TV software presets for `roku_tv`, `tcl_roku_tv`, `hisense_roku_tv`, and `generic_roku_tv`.
- Added `roku_ecp_port`, `roku_oppo_key`, and `roku_kodi_key` settings defaults.
- Used default Roku ECP port `8060`.
- Sent local HTTP POST requests to `/keypress/<key>`.
- Added strict allowlisting for Roku ECP input keys before URL construction.

## Behavior changed

No OPPO playback routing, service interception, `playercorefactory.xml` behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, Android / Google TV ADB preset metadata, TV-switching non-fatal behavior, or AVR sequencing changed.

## Behavior preserved

- Existing TV backend registry APIs.
- Existing Android / Google TV ADB preset metadata.
- Existing ADB command editability.
- Existing non-fatal TV switching behavior.
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

Roku ECP support is software-only until real device testing is supplied. Local control must be enabled on the Roku TV. Hardware validation is not claimed.
