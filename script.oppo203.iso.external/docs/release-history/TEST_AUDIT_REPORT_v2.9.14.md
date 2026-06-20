# Test Audit Report — v2.9.14 Final

Release gate verification summary (Windows dev machine, local `.venv`):

```text
Source checks: py_compile, render_docs --check, sync_version --check, test_layout.py --check, i18n_extract.py --check passed
Lint/format: ruff check clean; ruff format --check clean (55 files)
Full pytest: 1053 passed, 3 skipped (POSIX-only release scripts unavailable on Windows)
Coverage: TOTAL 99% across resources/lib (enforced gate fail_under=99)
Typing: mypy --strict gate passing (54 source files / 0 errors)
Release audit: PASS
```

The v2.9.14 changes add the six-option playback-architecture dispatch, the SVM3 (`#SVM 3`) verbose-mode monitor, richer `oppo203iso-status.json` session status, and robustness hardening, plus the supporting `resources/lib` sub-package split, `tv_*` rename, incremental `mypy --strict` rollout, and in-add-on menus delivered since v2.9.13. Version-pinned assertions were updated to 2.9.14 / "v2.9.14 Final" / build number 23; historical build-narrative and prior-release evidence references are unchanged.
