# Players DB schema — OPPO / clone player taxonomy

`players-models.json` is the configurator's canonical player-model database, adopted in the same
pattern as the TV database (`docs/configurator/tv-db/tv-models.json`): a `schema_version`ed
JSON consumed by the configurator, with a bundled copy at
`configurator/src/players-db/players-models.json` and this canonical copy kept **byte-identical**.

## Top-level

| Field | Meaning |
|---|---|
| `schema_version` | Breaking-change gate (currently `1`). Additive fields don't bump it; bump `db_version` instead. |
| `db_version` | `YYYY.MM.DD`, sortable. |
| `scope` | Purpose, granularity (`player_model_family`), validation status. |
| `region_schema` | The `regions` field contract and `allowed_values` (US/UK/EU/Asia). |
| `enum_order` | The 23 `oppo_hardware_model` enum ids in **`resources/settings.xml` order**. This order is install-base-critical (stored positionally) — append-only. |
| `families` | Configurator brand groups (display metadata + the UX-only `other` group). |
| `models` | The 23 player model families. |

## `families[]`
`id`, `name`, `ch` (logo glyph), `color`, `posture` (`stock`/`wake-rewrite`/`warning`). The
`other` family also carries `ui_models` — UX aliases that map onto an existing `hw` value.

## `models[]`
`key` (canonical, e.g. `UDP-203`), `hw` (settings enum id), `ui_label` (Step 2 picker label),
`label` (full), `brand`, `hardware_class`, `protocol_stance`, `wake_behavior`, `wake_command`,
`protocol_compatible`, `is_clone`, `is_reavon`, `is_successor`, `http_api_436`,
`src_supported[]`, `src_unsupported[]`, `nas_playback_candidate`, `aliases[]`, `regions[]`,
`validated`, `dolby_vision` (see below).

### New clone variants (2026.06.04)
`M9205-V2` / `-V3` / `-V4` mirror `M9205`, `M9702-Plus` mirrors `M9702`, and `VenPro-V203` is a
new `venpro`-family optical clone mirroring CineUltra — each **appended** to `enum_order`
(positional, install-base-safe) and wired end-to-end into the add-on registries, with
`tests/test_clone_variants_split.py` pinning the contract.

## `models[].dolby_vision`
Per-player Dolby Vision processing guidance, mirrored from the add-on's
`resources/lib/oppo/dolby_vision.py` (`DOLBY_VISION_PROFILES`) and pinned by
`tests/test_players_db_consistency.py`. Normalized controlled vocabularies:

| Field | Values | Meaning |
|---|---|---|
| `capable` | `yes` / `unknown` / `no` | Whether the device can output Dolby Vision at all. |
| `tv_led` | `official` / `expected` / `setup_sensitive` / `needs_validation` / `not_assessed` | TV-led DV stance. |
| `player_led` | `official` / `recommended_for_sony_lldv` / `available` / `not_assessed` | Player-led DV stance. |
| `confidence` | `high` / `medium` / `low` | Evidence strength (research, not hardware-validated). |

## `global_dv_rule`
A top-level, TV-type-driven processing rule (mirrors `DOLBY_VISION_TV_RULE`): full-DV TVs
(LG / Panasonic / Philips) default to **TV-led**; Sony / LLDV-style displays to
**Player-led / Auto**; unknown TVs test **auto → tv_led → player_led**; the DV FEL proof
source is **UHD ISO / BDMV** (never MKV).

### Recommended wording
> OPPO UDP-203/205 and OPPO-clone Chinoppo players are best validated with UHD ISO or full
> BDMV disc-folder sources. Dolby Vision TV-led output should not be blocked for the M9205
> family. Public evidence supports TV-led as the preferred mode for full-Dolby-Vision TVs
> such as LG / Panasonic / Philips, while Sony / LLDV-style displays may need Player-led or
> Auto. M9205 V1/V2/V3/V4 inherit the generic M9205-family capability only until exact-variant
> hardware validation is recorded.

## Source of truth + drift guard
This DB consolidates data that the add-on holds across `hardware_profiles.py`,
`hardware_capabilities.py`, `settings_reader.py` (`HARDWARE_COMPAT`, `ENUM_VALUES`, aliases),
`dolby_vision.py` (`DOLBY_VISION_PROFILES`, `DOLBY_VISION_TV_RULE`) and `resources/settings.xml`. `tests/test_players_db_consistency.py` asserts the JSON
faithfully reproduces those live registries, so the DB cannot silently drift from add-on
behavior. The add-on continues to run from its own registries (the TV DB follows the same
split — the add-on does not consume the JSON at runtime).

## Validation status
All rows are `validated: false`. Regions and the `dolby_vision` stances are a **candidate**
research mapping (sourced from `PLAYBRIDGE_CAPABILITY_SUMMARY.md`, S1-S9), not
hardware-validated; confirm per market and per display at setup.
