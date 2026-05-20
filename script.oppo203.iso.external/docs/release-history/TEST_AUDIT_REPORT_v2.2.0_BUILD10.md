# Test and Audit Report — v2.2.0 Build 10

Build 10 uses the improved verification workflow: each command is run separately, one command at a time. Because the local container's `ddtrace` pytest plugin previously caused timeout/hang behavior after successful test output, Build 10 disables that plugin for pytest-style verification with `-p no:ddtrace`.

## Source verification

```bash
python -m pytest -q -p no:ddtrace
```

```text
528 passed, 12 subtests passed
```

```bash
python -m unittest discover -s tests
```

```text
Ran 528 tests ... OK
```

```bash
python -m coverage run -m pytest -q -p no:ddtrace
python -m coverage report -m
```

```text
528 passed, 12 subtests passed
TOTAL 99%
```

```bash
python tools/audit_release.py --expected-version 2.2.0.10
```

```text
SUMMARY: PASS (104/104 checks passed)
```


## Post-unpack verification

Clean unpack verification from the generated Build 10 zip used the same improved command sequence.

```bash
python -m pytest -q -p no:ddtrace
```

```text
528 passed, 12 subtests passed
```

```bash
python -m unittest discover -s tests
```

```text
Ran 528 tests ... OK
```

```bash
python -m coverage run -m pytest -q -p no:ddtrace
python -m coverage report -m
```

```text
528 passed, 12 subtests passed
TOTAL 99%
```

```bash
python tools/audit_release.py --expected-version 2.2.0.10
```

```text
SUMMARY: PASS (104/104 checks passed)
```
