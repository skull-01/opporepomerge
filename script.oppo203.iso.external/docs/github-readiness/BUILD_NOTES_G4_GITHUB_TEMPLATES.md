# Build Notes — GitHub Readiness G4: GitHub Templates and Community Files

**Date:** 2026-05-20
**Project:** script.oppo203.iso.external
**Baseline:** script.oppo203.iso.external-2.9.10-github-g3-dev-source.zip
**Build:** GitHub Readiness G4
**Scope:** GitHub issue forms, pull request checklist, and community workflow structure.
**Runtime behavior changed:** No
**Hardware validation:** Not performed / not claimed

## Summary

G4 added structured GitHub community templates so future public collaboration can be triaged safely and consistently. The build did not change runtime Kodi behavior, OPPO routing, TV/AVR sequencing, service interception, packaging allowlist behavior, or hardware support claims.

## Files added

- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/ISSUE_TEMPLATE/documentation_fix.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/ISSUE_TEMPLATE/hardware_validation_report.yml`
- `.github/pull_request_template.md`

## Files changed

- `docs/README.md` — added a navigation note for the GitHub community templates.

## Template intent

- Bug reports request add-on version, Kodi version, platform, media type, route, steps, expected result, actual result, and redacted logs.
- Hardware-validation reports require real hardware evidence and exact model/firmware/connection/media/result details.
- Feature requests require scope and safety acknowledgement so protected v2.9.10 behavior is not changed casually.
- Documentation fixes include claim-safety acknowledgement to prevent accidental hardware-validation claims.
- Pull requests include protected-behavior, hardware-claim, validation, and handoff checklists.

## Validation summary

- YAML validation for `.github/**/*.yml`: passed.
- `python -m py_compile service.py default.py`: passed.
- `python tools/render_docs.py --check`: passed.
- `python tools/sync_version.py --check`: passed.
- `python tools/test_layout.py --check`: passed.
- `python tools/i18n_extract.py --check`: passed.
- `pytest -q tests/test_v2910_final_release.py`: 3 passed.
- `pytest -q tests/test_v2910*.py`: 189 passed.
- `python -m unittest discover -s tests`: 571 tests OK.
- `python tools/audit_release.py --expected-version 2.9.10`: PASS 553/553.
- Runtime ZIP audit: 68 runtime files, 0 forbidden directory policy violations, ZIP integrity passed.
- Post-unpack dev-source targeted validation: passed.

## Validation limitations

A broad split pytest attempt was made, but some test grouping attempts timed out in this environment before a complete aggregate summary could be captured. Because this build changed only GitHub templates and documentation navigation, no new coverage percentage is claimed. The inherited v2.9.10 Final software-verified coverage posture remains unchanged.

## Historical reconstruction entry

```yaml
build_id: GitHub Readiness G4
baseline: script.oppo203.iso.external-2.9.10-github-g3-dev-source.zip
scope: GitHub templates and community files
planned_success_rate: 95 percent
actual_outcome: successful
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
files_added:
  - .github/ISSUE_TEMPLATE/bug_report.yml
  - .github/ISSUE_TEMPLATE/config.yml
  - .github/ISSUE_TEMPLATE/documentation_fix.yml
  - .github/ISSUE_TEMPLATE/feature_request.yml
  - .github/ISSUE_TEMPLATE/hardware_validation_report.yml
  - .github/pull_request_template.md
files_changed:
  - docs/README.md
```
