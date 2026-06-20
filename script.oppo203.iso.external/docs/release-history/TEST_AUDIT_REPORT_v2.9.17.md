# Test Audit Report — v2.9.17 Final

Release gate verification summary (Windows dev machine, local `.venv`):

```text
Source checks: py_compile, render_docs --check, sync_version --check, test_layout.py --check, i18n_extract.py --check passed
Lint/format: ruff check clean; ruff format --check clean
Full pytest: 1219 passed, 3 skipped (POSIX-only release scripts unavailable on Windows)
Coverage: TOTAL 99% across resources/lib (enforced gate fail_under=99)
Typing: mypy --strict gate passing (51 source files / 0 errors)
Release audit: PASS
Configurator gate (player database touched): tsc -b clean; vitest 361 pass; vite build OK
```

The v2.9.17 changes add five OPPO-clone player variants end-to-end (M9205 V2/V3/V4, M9702 Plus, VenPro V203) and a cross-area Dolby Vision data layer (`resources/lib/oppo/dolby_vision.py` mirrored by the configurator's `players-models.json`, pinned by `tests/test_players_db_consistency.py`). New tests: `tests/test_clone_variants_split.py` and `tests/test_dolby_vision_capability.py`. Version-pinned assertions were updated to 2.9.17 / "v2.9.17 Final" / build number 26; historical build-narrative and prior-release evidence references are unchanged.
