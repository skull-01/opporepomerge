# Pull Request Checklist

## Summary

Describe the change in a few sentences. Include the build name if this PR is part of a GitHub Readiness build.

## Scope

- [ ] Documentation only
- [ ] Tests/tooling only
- [ ] Runtime code change
- [ ] Packaging/release change
- [ ] Hardware-validation evidence update

## Protected behavior

- [ ] I did not change protected playback/routing behavior unless explicitly documented.
- [ ] I did not change OPPO command payload behavior unless explicitly documented.
- [ ] I did not change TV/AVR sequencing behavior unless explicitly documented.
- [ ] I did not change runtime ZIP allowlist behavior unless explicitly documented.

## Hardware claim safety

- [ ] I did not claim hardware validation without real tester evidence.
- [ ] If hardware evidence was added, I updated the hardware-validation docs/matrix and linked evidence.

## Validation

Check every item that applies. Document anything not run.

- [ ] `python -m py_compile service.py default.py`
- [ ] `python tools/render_docs.py --check`
- [ ] `python tools/sync_version.py --check`
- [ ] `python tools/test_layout.py --check`
- [ ] `python tools/i18n_extract.py --check`
- [ ] `pytest -q tests/test_v2910_final_release.py`
- [ ] `pytest -q tests/test_v2910*.py`
- [ ] Full pytest or documented split pytest
- [ ] `python -m unittest discover -s tests`
- [ ] Coverage report generated when runtime/test code changed
- [ ] `python tools/audit_release.py --expected-version 2.9.10`
- [ ] Runtime ZIP audit confirms no tests/tools/scripts/docs/evidence/handoff files are included

## Documentation and handoff

- [ ] README/docs updated where needed
- [ ] Build notes updated where needed
- [ ] Release manifest updated where needed
- [ ] Test audit updated where needed
- [ ] Hardware-validation status updated or explicitly preserved
- [ ] AI handoff and historical reconstruction entry updated where needed

## Notes for reviewers

Add any risk, limitations, skipped checks, or follow-up work here.
