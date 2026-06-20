# Test and Audit Report — v2.2.0 Build 3

## Source verification

```bash
python -m pytest -q
```

```text
478 passed, 12 subtests passed in 14.66s
```

```bash
python -m unittest discover -s tests
```

```text
----------------------------------------------------------------------
Ran 478 tests in 13.715s

OK
```

```bash
python -m coverage run -m pytest -q
python -m coverage report -m
```

```text
TOTAL 99%
Raw combined line+branch coverage: 99.41275167785236%
```

```bash
python tools/audit_release.py --expected-version 2.2.0.3
```

```text
SUMMARY: PASS (73/73 checks passed)
```

## Post-unpack verification

```bash
python -m pytest -q
```

```text
478 passed, 12 subtests passed in 15.75s
```

```bash
python -m unittest discover -s tests
```

```text
----------------------------------------------------------------------
Ran 478 tests in 13.016s

OK
```

```bash
python -m coverage run -m pytest -q
python -m coverage report -m
```

```text
TOTAL 99%
Raw combined line+branch coverage: 99.41275167785236%
```

```bash
python tools/audit_release.py --expected-version 2.2.0.3
```

```text
SUMMARY: PASS (73/73 checks passed)
```

## Caveats

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested.
