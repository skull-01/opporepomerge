# Build Notes — v2.9.17 Final

Version 2.9.17 Final is a software-verified release that enriches the OPPO/clone player taxonomy after the v2.9.16 Final line. It adds five clone player variants end-to-end and introduces a cross-area Dolby Vision capability layer. The data is research-sourced (the OPPO/Chinoppo PlayBridge capability summary), every player row stays `validated: false`, no protected playback behavior changed, and the seven playback-architecture presets stay byte-identical.

## Scope

- **Five OPPO-clone player variants (ENH #341).** `M9205 V2 / V3 / V4` (mirroring the `M9205` eject-to-wake clone profile), `M9702 Plus` (mirroring `M9702`), and `VenPro V203` (a new `venpro`-family optical clone mirroring CineUltra) are appended to the `oppo_hardware_model` enum (positional, install-base-safe) and wired end-to-end across the add-on registries — `hardware_profiles.py`, `hardware_capabilities.py`, `settings_reader.py` (`ENUM_VALUES`, aliases, `HARDWARE_COMPAT`, the NAS-playback set), and `resources/settings.xml` — exactly as the merged `M9205-V1` split did. `tests/test_clone_variants_split.py` pins each variant (distinct enum value, alias normalization, compat mirrors its base, registry profile, clone-safe `#EJT` wake resolution).
- **Cross-area Dolby Vision data layer.** New `resources/lib/oppo/dolby_vision.py` holds `DOLBY_VISION_PROFILES` (per-player `capable` / `tv_led` / `player_led` / `confidence`, normalized controlled vocabularies) and the global `DOLBY_VISION_TV_RULE` (full-DV TVs → TV-led, Sony/LLDV → Player-led/Auto, unknown → auto→tv_led→player_led, proof source UHD ISO/BDMV, never MKV). The configurator's `players-models.json` mirrors this as a `dolby_vision` block on every model plus a top-level `global_dv_rule`, with `playersdb.ts` types. The data is read-only/advisory — nothing consumes it at runtime.
- **Cross-area drift guard.** `tests/test_players_db_consistency.py` now also pins the JSON `dolby_vision` data and `global_dv_rule` to the add-on registry both ways, so the configurator DB cannot drift from `dolby_vision.py`. New `tests/test_dolby_vision_capability.py` covers the module.
- **Source provenance.** The research is vendored at `docs/configurator/players-db/PLAYBRIDGE_CAPABILITY_SUMMARY.md`; `docs/configurator/players-db/PLAYERS_DB_SCHEMA.md` documents the new fields and the recommended wording.

## Preserved behavior

- The core protected behaviors remain unchanged: 4K/UHD disc-style interception only, loose/raw files stay with Kodi, conservative `playercorefactory.xml` routing, the canonical OPPO command map with no forbidden tokens (`#SIS`/`#PGU`/`#PGD`), NAS/AutoScript behavior, the Kodi startup auto-power guard, TV switching, and AVR sequencing.
- The runtime-only installable ZIP policy remains preserved.
- The seven-preset matrix stays a maintained cross-area contract and byte-identical; the new clone variants resolve to existing clone-safe control, so no existing configuration changes behavior.

## Hardware validation

This is a software-verified release. Real hardware validation was not performed or claimed. The Dolby Vision stances and the new clone-variant rows are research-grade and remain `validated: false`.
