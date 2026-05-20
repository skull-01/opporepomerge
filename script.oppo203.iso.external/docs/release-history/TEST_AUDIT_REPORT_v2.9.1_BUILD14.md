# Test Audit Report — v2.9.1 Build 14

## Source verification

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
type_check.py: passed / non-blocking skip when mypy unavailable
test_layout.py --check: passed
targeted Build 14 tests: 7 passed
pytest split run: 740 passed, 12 subtests passed
unittest discovery: 571 tests OK
coverage: TOTAL 99%
audit_release: PASS 339/339
```

## Notes

- Full pytest was run in split chunks because the single large process can hit local timeout behavior.
- Existing unittest `ResourceWarning` messages from inherited temporary-file fixture writes still appear, but the suite completes successfully.
- Metadata regression failures found during Build 14 were resolved by preserving historical phrases in `addon.xml`; no runtime behavior changed.
- Post-unpack verification must repeat the same checks from the unpacked dev-source package.
