# Players DB schema — OPPO / clone player taxonomy

`players.json` is the configurator's canonical player-model database, adopted in the same
pattern as the TV database (`docs/configurator/tv-db/tv-models.json`): a `schema_version`ed
JSON consumed by the configurator, with a bundled copy at
`configurator/src/players-db/players.json` and this canonical copy kept **byte-identical**.

## Top-level

| Field | Meaning |
|---|---|
| `schema_version` | Breaking-change gate (currently `1`). Additive fields don't bump it; bump `db_version` instead. |
| `db_version` | `YYYY.MM.DD`, sortable. |
| `scope` | Purpose, granularity (`player_model_family`), validation status. |
| `region_schema` | The `regions` field contract and `allowed_values` (US/UK/EU/Asia). |
| `enum_order` | The 18 `oppo_hardware_model` enum ids in **`resources/settings.xml` order**. This order is install-base-critical (stored positionally) — append-only. |
| `families` | Configurator brand groups (display metadata + the UX-only `other` group). |
| `models` | The 18 player model families. |

## `families[]`
`id`, `name`, `ch` (logo glyph), `color`, `posture` (`stock`/`wake-rewrite`/`warning`). The
`other` family also carries `ui_models` — UX aliases that map onto an existing `hw` value.

## `models[]`
`key` (canonical, e.g. `UDP-203`), `hw` (settings enum id), `ui_label` (Step 2 picker label),
`label` (full), `brand`, `hardware_class`, `protocol_stance`, `wake_behavior`, `wake_command`,
`protocol_compatible`, `is_clone`, `is_reavon`, `is_successor`, `http_api_436`,
`src_supported[]`, `src_unsupported[]`, `nas_playback_candidate`, `aliases[]`, `regions[]`,
`validated`.

## Source of truth + drift guard
This DB consolidates data that the add-on holds across `hardware_profiles.py`,
`hardware_capabilities.py`, `settings_reader.py` (`HARDWARE_COMPAT`, `ENUM_VALUES`, aliases)
and `resources/settings.xml`. `tests/test_players_db_consistency.py` asserts the JSON
faithfully reproduces those live registries, so the DB cannot silently drift from add-on
behavior. The add-on continues to run from its own registries (the TV DB follows the same
split — the add-on does not consume the JSON at runtime).

## Validation status
All rows are `validated: false`. Regions are a **candidate** research mapping, not
hardware-validated; confirm per market at setup.
