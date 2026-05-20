# Build Notes — v2.2.0 Build 1

```yaml
addon_version: 2.2.0.1
build: v2.2.0-build1
baseline: script.oppo203.iso.external-2.1.0-build8.zip
focus: first gradual v1.1.9 + v0.9.14 superset-merge slice
scope: restore v0.9.14 compatibility helper API and service settings watcher
full_merge_started: partial only; broad full merge not started
real_hardware_tested: false
```

## Changes

- Added `resources/lib/first_run_wizard.py` compatibility helper module.
- Added service `Monitor.onSettingsChanged()` compatibility reapply watcher.
- Added `oppo_jailbreak_enabled` and `oppo_autoscript_shell_handler` settings/defaults/strings.
- Added tests for clone preset application, Reavon warning-only behavior, AutoScript warning text, service watcher no-op path, model-change path, and jailbreak-toggle path.

## Stability notes

- No full feature union was attempted.
- Existing v2 External Player, wake rewrite, TV switching, fake OPPO server tests, and 99% coverage gate were preserved.
