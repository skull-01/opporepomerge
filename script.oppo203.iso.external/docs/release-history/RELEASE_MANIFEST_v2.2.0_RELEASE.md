# Release Manifest — v2.2.0

Package: `script.oppo203.iso.external-2.2.0.zip`
Checksum file: `script.oppo203.iso.external-2.2.0.sha256`
Baseline: `script.oppo203.iso.external-2.2.0-build12.zip`
Version in `addon.xml`: `2.2.0`

## Release status

Software merge-complete candidate packaged as v2.2.0. Real hardware validation is deferred to the user after this package.

## Required verification

- `python -m pytest -q -p no:ddtrace`
- `python -m unittest discover -s tests -q`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m coverage run -m pytest -q -p no:ddtrace`
- `python -m coverage report -m`
- `python tools/audit_release.py --expected-version 2.2.0`

These commands must pass from source and from a clean unpack of the generated zip.
