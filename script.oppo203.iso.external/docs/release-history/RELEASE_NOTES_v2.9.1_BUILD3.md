# Release Notes — v2.9.1 Build 3

Build 3 externalizes the canonical OPPO remote command map into `resources/data/oppo_command_map.json` and validates it through `resources/lib/command_map.py`.

This is a cleanup and maintainability build. It does not change OPPO command semantics, playback behavior, XML routing behavior, NAS playback behavior, or startup auto-power behavior.

The command map remains the protected 76-key map and continues to forbid `#SIS`, `#PGU`, and `#PGD`.
