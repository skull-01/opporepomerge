# Build Notes — v2.2.0 Build 3

Version: `2.2.0.3`
Baseline: `script.oppo203.iso.external-2.2.0-build2.zip`

## Purpose

Continue the v1.1.9 + v0.9.14 superset merge gradually by restoring the v0.9.14 service/wizard warning logging slice.

## Changes

- Added `collect_compatibility_warnings()` to the narrow `first_run_wizard.py` compatibility helper module.
- Extended `service.Monitor` to track `oppo_autoscript_shell_handler`.
- Logged AutoScript verbose-push warnings when that setting changes outside the wizard.
- Added Build 3 tests for warning collection and service watcher behavior.

## Scope

No broad merge, no real hardware testing, and no command-map expansion were performed.
