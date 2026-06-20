# Build Notes — v2.9.1 Build 3

## Target

Externalize the canonical OPPO remote command map safely while preserving all runtime command semantics.

## Baseline

- Baseline: `script.oppo203.iso.external-2.9.1-build2-dev-source.zip`
- Previous build: v2.9.1 Build 2 centralized disc classification and shared constants.

## Scope

Implemented recommendation #5 and additional safe constant cleanup from recommendation #8:

- Added `resources/data/oppo_command_map.json` as the canonical 76-key OPPO command-map data file.
- Added `resources/lib/command_map.py` with a validated `CommandMap` wrapper and loader helpers.
- Updated `settings_reader.DEFAULTS["oppo_remote_command_map"]` to expose the externalized map as compact JSON for backward compatibility.
- Updated `oppo_remote.DEFAULT_COMMAND_MAP` to load from the validated command-map helper.
- Updated `tools/audit_release.py` to validate the externalized command map through the loader rather than through inline settings data.
- Added focused Build 3 tests for file existence, 76-key size, forbidden-token rejection, settings compatibility, default remote behavior, and custom override merging.

## Behavior preserved

No playback behavior changed. The command keys and values remain canonical, including `bluray_input=#SRC 0`, `page_up=#PUP`, `page_down=#PDN`, `power_on=#PON`, and `eject=#EJT`. Reavon warning-only behavior, Chinoppo/M9702 wake rewrite behavior, stock OPPO pass-through behavior, startup auto-power, Option 4 XML routing, and 4K disc-style interception remain unchanged.

## Hardware validation

No real OPPO, Chinoppo/M9702/M920x, Kodi, NAS, TV, or ADB hardware validation was performed or claimed.
