# Build Notes — Version 2.0.0 Build 3

## Target

Continue the v2.0 MVP hardening path from Build 2.

## Baseline

- Input package: `script.oppo203.iso.external-2.0.0-build2.zip`
- Baseline test result before edits: `324 / 324 passing`

## Build 3 scope

Build 3 implements the staged Kodi API mocking foundation from the v2 roadmap.

Implemented:

- Test-only local Kodi stubs under `tests/_stubs/`.
- Opt-in stub context in `tests/test_kodi_stubs.py`.
- Stub-backed import smoke tests for `default.py`, `service.py`, and `resources.lib.installer`.
- CI coverage report changed to staged/non-blocking mode while stubbed coverage is expanded.

Not implemented:

- Final 92% hard coverage gate.
- Physical hardware validation.

## Tests

```text
python -m pytest -q
331 passed

python -m unittest discover -s tests
331 passed
```

## Audit

```text
python -m compileall .
addon.xml parses
resources/settings.xml parses
locale parity passes across 12 locale files
command map has 76 keys and no #SIS/#PGU/#PGD
hardware enum count matches HARDWARE_COMPAT count: 12/12
```

## Package

Output package:

```text
script.oppo203.iso.external-2.0.0-build3.zip
```
