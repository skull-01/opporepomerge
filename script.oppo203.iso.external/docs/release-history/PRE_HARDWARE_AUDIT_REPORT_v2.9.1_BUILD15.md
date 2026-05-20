# PRE-HARDWARE AUDIT REPORT — v2.9.1 Build 15

## Software audit status

```text
Source py_compile: passed
Source render_docs --check: passed
Source sync_version --check: passed
Source type_check.py: passed / non-blocking skip when mypy unavailable
Source test_layout.py --check: passed
Source i18n_extract.py --check: passed
Source targeted Build 15 tests: 7 passed
Source pytest split run: 747 passed, 12 subtests passed
Source unittest discovery: 571 tests OK
Source coverage: TOTAL 99%
Source audit_release: PASS 350/350

Post-unpack py_compile: passed
Post-unpack render_docs --check: passed
Post-unpack sync_version --check: passed
Post-unpack type_check.py: passed / non-blocking skip when mypy unavailable
Post-unpack test_layout.py --check: passed
Post-unpack i18n_extract.py --check: passed
Post-unpack targeted Build 15 tests: 7 passed
Post-unpack pytest split run: 747 passed, 12 subtests passed
Post-unpack unittest discovery: 571 tests OK
Post-unpack coverage: TOTAL 99%
Post-unpack audit_release: PASS 350/350
```

## Hardware status

No real OPPO, Chinoppo/M9702/M920x, Kodi, NAS, TV, ADB, or RF/IR/BT bridge hardware validation was performed or claimed.

## Protected behavior expected to remain unchanged

- 4K/UHD/2160p disc-style interception only.
- Loose/raw video files stay with Kodi.
- Option 4 conservative playercorefactory.xml behavior.
- Canonical 76-key OPPO command map.
- No forbidden OPPO command tokens #SIS #PGU #PGD.
- Reavon warning-only behavior.
- Chinoppo/M9702 wake rewrite behavior.
- Stock OPPO pass-through behavior.
- Kodi startup auto-power guard behavior.
- NAS adapter behavior.
- Runtime-only installable ZIP policy.
