# Coverage Report — v2.5.3 Build 2

```yaml
build: v2.5.3 Build 2
coverage_gate: 99 percent
source_result: TOTAL 99%
post_unpack_dev_source_result: TOTAL 99%
covered_scope: resources/lib with branch coverage per existing .coveragerc
```

## Source coverage command

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
```

## Source result

```text
624 passed, 12 subtests passed
TOTAL 99%
```

## Post-unpack dev-source result

```text
624 passed, 12 subtests passed
TOTAL 99%
```

The 99 percent gate remains satisfied after adding Option 4 XML rule tests and wizard/installer naming guidance.
