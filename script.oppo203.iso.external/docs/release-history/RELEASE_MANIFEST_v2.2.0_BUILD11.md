# Release Manifest — v2.2.0 Build 11

```yaml
version: 2.2.0.11
artifact: script.oppo203.iso.external-2.2.0-build11.zip
baseline: script.oppo203.iso.external-2.2.0-build10.zip
scope: narrow wizard/UI compatibility-warning reconciliation slice
coverage_gate: 99 percent
full_merge_status: in_progress_not_complete
```

## Required verification

- `python -m pytest -q -p no:ddtrace`
- `python -m unittest discover -s tests`
- `python -m coverage run -m pytest -q -p no:ddtrace`
- `python -m coverage report -m`
- `python tools/audit_release.py --expected-version 2.2.0.11`
