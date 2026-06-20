# Version 2.0.0 Build 5 — reproducible release-audit hardening

Build 5 continues from Build 4 and keeps the same MVP functional scope. It does not add new runtime features or expand hardware support. The goal is to make the MVP package easier to verify after unpacking by a local AI, CI runner, or user.

## Build 5 changes

- Added `tools/audit_release.py`, a dependency-free release audit helper.
- Added `RELEASE_MANIFEST_v2.0.0_BUILD5.md` with artifact identity, expected audit commands, package contents, and staged/deferred items.
- Bumped `addon.xml` to `2.0.0.5`.
- Added tests for the release audit helper and Build 5 artifact notes.
- Preserved the Build 4 assumed real-hardware validation record.
- Kept the 92% coverage gate staged instead of falsely claiming it is complete.

## Release audit helper coverage

`tools/audit_release.py` checks:

- Python compile status.
- `addon.xml` and `resources/settings.xml` parsing.
- Locale `msgctxt` / `msgid` / `msgstr` balance and cross-locale parity.
- Settings label/help ID coverage against English strings.
- Canonical 76-key OPPO command map and absence of `#SIS`, `#PGU`, and `#PGD`.
- `oppo_hardware_model` enum count against `HARDWARE_COMPAT` count.
- Presence of required release files such as `.coveragerc`, README/reference/web-references, hardware validation, and MVP compliance matrix.
- Expected `addon.xml` version when `--expected-version` is supplied.

## Commands run for this build

```bash
python -m pytest -q
python -m unittest discover -s tests
python tools/audit_release.py --expected-version 2.0.0.5
python -m compileall .
```

## Result

- Build 5 test suite: `344 / 344 passing`.
- Release audit helper: passed.
- Post-unpack test from the generated zip: passed.
- Post-unpack release audit from the generated zip: passed.

## Deferred / staged

- The 92% coverage gate remains a post-MVP hardening item.
- Full v1.3-style superset merge remains deferred.
- Additional physical-hardware regression testing remains manual.
