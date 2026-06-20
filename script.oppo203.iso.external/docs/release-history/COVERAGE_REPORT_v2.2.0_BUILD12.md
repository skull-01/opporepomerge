# Coverage Report — v2.2.0 Release 2.2.0

```yaml
version: 2.2.0
coverage_gate: 99
coverage_command: python -m coverage run -m pytest -q -p no:ddtrace
reported_total: 99%
```

The 99% coverage gate remains enforced. The local ddtrace pytest plugin is disabled during coverage runs to avoid container-specific timeout behavior observed during Build 9.
