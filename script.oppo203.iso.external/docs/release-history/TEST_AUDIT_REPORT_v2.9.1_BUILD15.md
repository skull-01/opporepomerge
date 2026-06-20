# TEST AND AUDIT REPORT — v2.9.1 Build 15

## Source verification

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
type_check.py: passed / non-blocking skip when mypy unavailable
test_layout.py --check: passed
i18n_extract.py --check: passed
targeted Build 15 tests: 7 passed
pytest split run: 747 passed, 12 subtests passed
unittest discovery: 571 tests OK
coverage: TOTAL 99%
audit_release: PASS 350/350
```

A single-process full pytest command reached the local timeout near completion. Build 15 therefore used the established split verification path: `tests/test_all.py` plus the remaining `tests/test_*.py` files.

## Post-unpack dev-source verification

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
type_check.py: passed / non-blocking skip when mypy unavailable
test_layout.py --check: passed
i18n_extract.py --check: passed
targeted Build 15 tests: 7 passed
pytest split run: 747 passed, 12 subtests passed
unittest discovery: 571 tests OK
coverage: TOTAL 99%
audit_release: PASS 350/350
```

## Build 15 targeted test coverage

`tests/test_v291_build15_i18n_extraction_transition.py` validates:

- `tools/i18n_extract.py` preserves the `tools/make_pot.py` fallback contract.
- The facade renders deterministic Kodi `msgctxt` templates without requiring Babel.
- CLI `--check` is non-writing and safe.
- `babel.cfg` and `scripts/verify.sh` wire the transition.
- Runtime ZIP packaging excludes Build 15 development-only i18n tooling.
- Release audit discovers the Build 15 manifest and evidence files.
- Active version metadata identifies `v2.9.1 Build 15`.

Hardware validation is not claimed.
