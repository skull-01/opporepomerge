# GitHub Readiness Build G3 — Developer Documentation Pack

**Project:** `script.oppo203.iso.external`
**Version:** `2.9.10`
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g2-dev-source.zip`
**Build type:** documentation-only GitHub readiness build
**Runtime behavior changed:** false
**Hardware validation:** not performed / not claimed


## Coverage status

No new G3 coverage result is claimed.

Reason: G3 changed documentation only and the environment already showed timeout risk on long full-suite commands. The protected v2.9.10 Final baseline previously recorded TOTAL 99% coverage. G3 did not change runtime source modules, so there is no code coverage delta to report.

## Rule for future builds

A future tooling or code build should run `coverage run -m pytest` and `coverage report` when practical. Do not claim a new coverage percentage unless the command completes.
