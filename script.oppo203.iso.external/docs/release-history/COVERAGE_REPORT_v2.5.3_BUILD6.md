# Coverage Report — v2.5.3 Build 6

```yaml
coverage_gate: 99 percent
source_result: TOTAL 99%
post_unpack_result: TOTAL 99%
pytest_result_under_coverage: 648 passed, 12 subtests passed
```

Build 6 preserves the enforced 99 percent coverage gate. It is a packaging/evidence freeze and does not add runtime behavior.

## Source coverage command

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
```

## Source result

```text
648 passed, 12 subtests passed
TOTAL 99%
```

## Post-unpack coverage result

```text
648 passed, 12 subtests passed
TOTAL 99%
```
