# v2.9.10 Build 16 — AVR wizard, diagnostics, and safety UI

v2.9.10 Build 16 adds AVR setup UI helpers, query-only AVR test actions, explicit user-action gates for power/input tests, sanitized AVR diagnostic export, and safety wording. AVR support remains disabled by default, AVR power-off and volume automation remain disabled by default, no AVR playback sequencing hook is added, diagnostics sanitize credentials and state hardware_validation_claimed=false, and hardware validation is not claimed.

## Verification result

```text
source checks: passed
targeted Build 16 tests: 15 passed
all v2.9.10 tests: 167 passed
focused AVR wizard/diagnostics regression tests: 15 passed
source coverage: TOTAL 99%
audit_release: PASS 525/525
```

Post-unpack verification uses the Balanced Gate: py_compile, targeted Build 16 tests, and audit_release unless failure requires deeper verification.
