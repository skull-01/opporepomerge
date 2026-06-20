# Coverage Report — v2.9.10 Build 5

```yaml
coverage_gate: 99
source_total: 99%
post_unpack_total: 99%
```

Build 5 preserved the enforced 99% coverage gate after adding the TV backend registry and TV preset registry. Coverage was measured with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and `-p no:ddtrace` using split coverage runs to avoid local plugin/runtime timeouts.

## Source result

```text
TOTAL 3888 statements, 40 missed, 1312 branches, 28 partial branches, 99% coverage
```

## Post-unpack result

```text
TOTAL 3888 statements, 40 missed, 1312 branches, 28 partial branches, 99% coverage
```
