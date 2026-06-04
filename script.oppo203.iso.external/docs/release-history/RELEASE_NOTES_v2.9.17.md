# Release Notes — v2.9.17 Final

Version 2.9.17 Final is a software-verified release that enriches the OPPO/clone player taxonomy from the PlayBridge capability summary. No new playback presets or persistent-setting categories are added; the seven-preset matrix and the protected playback behaviors stay intact.

## Highlights

- **Five new OPPO-clone player variants** — `M9205 V2 / V3 / V4` (mirroring M9205), `M9702 Plus` (mirroring M9702), and `VenPro V203` (a new `venpro` family mirroring CineUltra) are added end-to-end and appended to the `oppo_hardware_model` enum, so they can be selected in the configurator and resolve to the correct clone-safe (`#EJT`) control.
- **Cross-area Dolby Vision capability layer** — a new add-on `dolby_vision` registry (`DOLBY_VISION_PROFILES` + a global TV-type rule) mirrored by `dolby_vision` fields and a `global_dv_rule` in the configurator's player database, with a consistency guard. Per-player `capable` / `tv_led` / `player_led` / `confidence` guidance: full-DV TVs (LG/Panasonic/Philips) prefer TV-led, Sony/LLDV displays prefer Player-led/Auto, and DV is validated with UHD ISO / BDMV, never MKV.
- **Research provenance + schema docs** — the capability summary is vendored under `docs/`, and the players-DB schema documents the new fields and recommended wording.

## Runtime behavior

The player taxonomy that the add-on resolves at runtime gains five recognized clone models (each resolving to existing clone-safe control); no existing configuration changes behavior, and the Dolby Vision layer is advisory data that nothing consumes at runtime. The seven playback-architecture presets, the playback dispatch, the canonical OPPO command map, conservative `playercorefactory.xml` routing, NAS/AutoScript behavior, startup auto-power, TV switching, and AVR sequencing are preserved and byte-identical.

## Hardware validation

This package remains software-verified only. The new clone variants and the Dolby Vision stances are research-sourced and device/display-dependent; hardware validation is not performed / not claimed. Every player row stays `validated: false`.
