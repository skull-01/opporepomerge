# Coverage Report G2

**Build:** GitHub Readiness G2 — Public Documentation Pack
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip`
**Output line:** `script.oppo203.iso.external-2.9.10-github-g2`
**Runtime behavior changed:** `false`
**Hardware validation:** `not_performed_not_claimed`
**Generated:** 2026-05-20

## Coverage status

G2 is a public documentation and test-layout compatibility build. It did not change runtime modules.

A coverage run based only on unittest discovery completed but produced 70% total coverage because unittest discovery does not exercise the complete pytest-based coverage suite. That result is not used as a release coverage gate.

A split parallel coverage attempt was started to reproduce the hard gate, but it timed out before completion in this environment. Therefore:

```text
G2 coverage gate rerun: not completed
New coverage claim: none
Inherited v2.9.10 Final coverage evidence: unchanged
Runtime behavior changed: false
```

Do not use G2 as a new coverage-gate proof. Use the completed split pytest, unittest, audit, runtime ZIP audit, and post-unpack verification listed in `TEST_AUDIT_REPORT_G2.md` for this documentation-only build.
