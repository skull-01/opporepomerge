# Coverage Report — Version 2.9.0

```yaml
coverage_gate: 99 percent
expected_result: TOTAL 99%
coverage_command: PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
```

The v2.9.0 release rebuild preserves the 99 percent coverage gate from the v2.5.3 Build 6 baseline. Final measured source and post-unpack results are recorded in `TEST_AUDIT_REPORT_v2.9.0.md` and the assistant build summary.
## Source verification results

```text
py_compile: passed
targeted v2.9.0 tests: 5 passed
pytest: 653 passed, 12 subtests passed
unittest: 571 tests OK
coverage: TOTAL 99%
release audit: PASS 217/217 checks passed
```
## Post-unpack dev-source verification results

```text
py_compile: passed
targeted v2.9.0 tests: 5 passed
pytest: 653 passed, 12 subtests passed
unittest: 571 tests OK
coverage: TOTAL 99%
release audit: PASS 217/217 checks passed
runtime ZIP audit: passed; 45 runtime files; 0 forbidden evidence/test/tool files
```
