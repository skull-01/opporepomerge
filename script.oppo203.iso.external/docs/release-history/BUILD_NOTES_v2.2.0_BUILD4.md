# Build Notes — v2.2.0 Build 4

```yaml
addon_version: 2.2.0.4
artifact: script.oppo203.iso.external-2.2.0-build4.zip
baseline: script.oppo203.iso.external-2.2.0-build3.zip
release_line: v2.2 gradual v1.1.9 + v0.9.14 superset merge
scope: service watcher persistence slice
coverage_gate: 99
```

## Summary

Build 4 continues the gradual v1.1.9 + v0.9.14 superset merge without starting a broad rewrite. This slice makes the restored v0.9.14 service settings watcher persist compatibility-preset changes when a user changes the hardware model outside the wizard.

## Stability-first changes

- Added `settings_reader.save_settings(addon_data_dir, settings)`.
- Updated `service.Monitor.onSettingsChanged()` to persist applied compatibility presets when an add-on data directory is available.
- Kept Reavon warning-only behavior: warning-only model changes do not write OPPO command mutations.
- Preserved the existing `[v0.9.14-warning]` support-log behavior.
- Preserved the 99% coverage gate.

## Issue fixed or hardened

Previously, the restored v0.9.14 watcher reapplied compatibility presets to the in-memory settings object. Build 4 makes clone preset changes durable by saving the updated settings XML when actual preset mutations occur. Save failures remain non-fatal and are logged.

## Tests added

`tests/test_superset_merge_build4.py` adds coverage for:

- `save_settings()` file creation.
- `save_settings()` update of existing rows.
- Runtime/private-key skipping during persistence.
- Service watcher persistence of clone preset mutations.
- Reavon warning-only behavior without command-map mutation persistence.
- Build 4 version identity.

## Commands run

```bash
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.2.0.4
```

## Caveats

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested.

The full v1.1.9 + v0.9.14 superset merge remains in progress.
