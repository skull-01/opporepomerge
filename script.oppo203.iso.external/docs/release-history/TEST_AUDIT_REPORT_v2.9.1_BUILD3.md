# Test Audit Report — v2.9.1 Build 3

## Source verification

```text
py_compile: passed
targeted Build 3 tests: 6 passed
pytest split run: 674 passed, 12 subtests passed
unittest: 571 tests OK
coverage: TOTAL 99%
release audit: PASS 238/238
```

Full pytest was executed in two chunks (`tests/test_all.py` and all remaining `test_*.py` files) because the single-process full-suite invocation hit the local container timeout after passing most tests. The split execution covers the same collected test files and completed successfully.

## Post-unpack dev-source verification

```text
py_compile: passed
targeted Build 3 tests: 6 passed
pytest split run: 674 passed, 12 subtests passed
unittest: 571 tests OK
coverage: TOTAL 99%
release audit: PASS 238/238
```

## Runtime ZIP audit

```text
runtime files: 49
forbidden tests/tools/reports/handoff/evidence files: 0
zip integrity: passed
resources/data/oppo_command_map.json included: yes
```
