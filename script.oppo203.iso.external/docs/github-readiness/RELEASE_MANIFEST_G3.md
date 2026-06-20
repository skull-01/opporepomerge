# GitHub Readiness Build G3 — Developer Documentation Pack

**Project:** `script.oppo203.iso.external`
**Version:** `2.9.10`
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g2-dev-source.zip`
**Build type:** documentation-only GitHub readiness build
**Runtime behavior changed:** false
**Hardware validation:** not performed / not claimed


## Package outputs

- `script.oppo203.iso.external-2.9.10-github-g3.zip`
- `script.oppo203.iso.external-2.9.10-github-g3-dev-source.zip`
- `script.oppo203.iso.external-2.9.10-github-g3-artifacts-bundle.zip`
- `script.oppo203.iso.external-2.9.10-github-g3.sha256`

## Files added / updated

- `docs/developer-guide/README.md`
- `docs/developer-guide/architecture.md`
- `docs/developer-guide/testing.md`
- `docs/developer-guide/packaging.md`
- `docs/developer-guide/release-process.md`
- `docs/developer-guide/code-quality.md`
- `docs/developer-guide/ai-maintainer-rules.md`
- `docs/hardware-validation/hardware-validation-plan.md`
- `docs/hardware-validation/hardware-support-matrix.md`
- `docs/README.md`

## Runtime ZIP contents

Runtime ZIP audit found 68 runtime files, 0 forbidden development/evidence/docs files, and valid ZIP integrity.

## Reconstruction

Start from `script.oppo203.iso.external-2.9.10-github-g2-dev-source.zip`, add the developer guide and hardware-validation documentation listed above, update `docs/README.md`, run validation, package with `BUILD_SUFFIX=github-g3`, then create this manifest and handoff artifacts.
