# Developer Guide — Testing

## Goal

The project has a strong test culture. v2.9.10 Final was software-verified before GitHub readiness began. GitHub-readiness builds must preserve that posture and record any limitations honestly.

## Recommended local validation sequence

Run from the repository root:

```bash
python -m py_compile service.py default.py
python tools/render_docs.py --check
python tools/sync_version.py --check
python tools/test_layout.py --check
python tools/i18n_extract.py --check
pytest -q tests/test_v2910_final_release.py
pytest -q tests/test_v2910*.py
pytest -q
python -m unittest discover -s tests
python tools/audit_release.py --expected-version 2.9.10
```

If the full `pytest -q` run times out locally, split it into smaller groups and document the split strategy in the test audit report.

## GitHub Actions CI

Build G6 adds a GitHub Actions workflow in `.github/workflows/ci.yml`. The workflow runs the release-gate checks in CI through the `test` job, including targeted tests, full pytest, unittest discovery, coverage, release audit, runtime ZIP audit, and a dev-source post-unpack smoke gate.

CI failures should be treated as blockers unless an environmental limitation is clearly documented. CI results are software evidence only and do not count as real hardware validation.

## Coverage

The protected v2.9.10 Final release evidence recorded 99% coverage. GitHub-readiness documentation-only builds may inherit that baseline only when no runtime code changed and the coverage run times out. Do not claim a new coverage result unless coverage actually ran to completion.

Suggested command:

```bash
coverage run -m pytest
coverage report
```

## Targeted tests

Use targeted tests for fast safety checks:

```bash
pytest -q tests/test_v2910_final_release.py
pytest -q tests/test_v2910*.py
```

These tests are especially useful during documentation/layout changes because they verify current-line identity, release evidence, and v2.9.10 behavior expectations.

## Release audit

The release audit is a required gate:

```bash
python tools/audit_release.py --expected-version 2.9.10
```

The audit protects release evidence, package policy, version identity, and other final-release invariants.

## Runtime ZIP audit

After packaging, inspect the runtime ZIP. It must not include development-only content.

Forbidden runtime content:

- tests
- tools
- scripts
- docs
- release-evidence
- handoff files
- reports
- coverage files

## Post-unpack verification

For release or handoff builds, verify the dev-source package after unpacking it into a clean directory. At minimum run:

```bash
python tools/sync_version.py --check
pytest -q tests/test_v2910*.py
python tools/audit_release.py --expected-version 2.9.10
```

## Test report rule

Every build must produce a `TEST_AUDIT_REPORT_*.md` file containing:

- commands run
- pass/fail/timeout result
- environment limitations
- whether runtime behavior changed
- whether hardware validation was performed
