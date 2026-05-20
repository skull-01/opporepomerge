# Coverage Report — v2.9.1 Build 2

```text
Source coverage: TOTAL 99%
Coverage gate: fail_under = 99
```

Coverage was measured with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and `-p no:ddtrace`. Because the full single coverage invocation hit the local container timeout after the tests completed, coverage data was collected in one-command-at-a-time chunks and appended into a single `.coverage` data file before running `coverage report -m`.

The resulting report showed `TOTAL 99%`, satisfying the existing gate.
