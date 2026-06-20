# Release Manifest — v2.2.0 Build 2

artifact_name: script.oppo203.iso.external-2.2.0-build2.zip
addon_version: 2.2.0.2
baseline: script.oppo203.iso.external-2.2.0-build1.zip
sha256: TBD-after-packaging

## Verification commands

```bash
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.2.0.2
```

## Merge status

Gradual superset merge in progress. Build 2 ports v0.9.14 hardware test coverage and hardens release audit behavior.
