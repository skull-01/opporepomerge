# Release Manifest — v2.2.0 Build 8

```yaml
addon_version: 2.2.0.8
package: script.oppo203.iso.external-2.2.0-build8.zip
checksum_file: script.oppo203.iso.external-2.2.0-build8.sha256
baseline: script.oppo203.iso.external-2.2.0-build7.zip
handoff: Combined_DevLog_and_Addon_Research_v22_Handoff.md
```

## Required verification

```bash
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.2.0.8
```

The generated package must be unpacked into a clean directory and the same commands must pass from the packaged artifact.
