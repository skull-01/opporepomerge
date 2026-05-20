# Release Manifest — v2.2.0 Build 6

| Field | Value |
|---|---|
| Add-on version | `2.2.0.6` |
| Package | `script.oppo203.iso.external-2.2.0-build6.zip` |
| Baseline | `script.oppo203.iso.external-2.2.0-build5.zip` |
| Merge slice | Active wizard compatibility-warning integration |
| Coverage gate | 99% |

## Expected verification

- `python -m pytest -q`
- `python -m unittest discover -s tests`
- `python -m coverage run -m pytest -q`
- `python -m coverage report -m`
- `python tools/audit_release.py --expected-version 2.2.0.6`
