# Coverage Report — v2.1.0 Build 1

Coverage was measured with branch coverage enabled for `resources/lib` using:

```text
python -m coverage erase
python -m coverage run -m pytest -q
python -m coverage report -m
```

Observed result before enforcing the new gate:

```text
378 passed
TOTAL 2516 statements, 163 missed, 894 branches, 114 partial branches, 92% coverage
```

`.coveragerc` now enforces:

```text
fail_under = 92
```

The 92 percent coverage gate is therefore no longer staged for this build line; it is enforced for the measured library coverage profile.
