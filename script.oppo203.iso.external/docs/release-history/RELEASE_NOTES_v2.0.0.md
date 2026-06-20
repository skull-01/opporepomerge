# RELEASE NOTES — script.oppo203.iso.external v2.0.0 Final

## Release identity

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.0.0
release_line: v2.0 MVP
source_baseline: verified Build 6 line
artifact_name: script.oppo203.iso.external-2.0.0.zip
checksum_name: script.oppo203.iso.external-2.0.0.sha256
release_status: final MVP package
```

## Summary

Version 2.0.0 is the stable MVP release packaged from the verified Build 6 source line. It preserves the tested v2 MVP behavior and returns the installable package identity to the final public version `2.0.0`.

## Included MVP behavior

- External Player MVP flow.
- M9702 / Chinoppo wake rewrite from `#PON` and `#POW` to `#EJT`.
- Stock OPPO `#PON` / `#POW` pass-through.
- TCL / Android TV ADB switching in the External Player flow.
- Non-fatal TV switching failure handling.
- Session sentinel cleanup.
- Fake OPPO TCP server regression tests.
- Kodi stub import coverage for normal Python test runs.
- Release audit tooling and post-unpack verification.

## Real hardware validation

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or ADB hardware validation is claimed for this package. Per the release decision, real hardware testing is deferred until after the later full v1.1.9 + v0.9.14-style merge.

## Deferred work

- Raise the 92% coverage gate after deeper Kodi-bound tests exist.
- Complete the full v1.1.9 + v0.9.14 strict superset merge.
- Add the remaining unique v0.9.14 hardware/service watcher tests.
- Perform real hardware validation after the full merge.
- Prepare repository submission packaging if desired.

## Verification commands

```bash
python -m pytest -q
python -m unittest discover -s tests
python tools/audit_release.py --expected-version 2.0.0
```
