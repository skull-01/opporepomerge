# Coverage Report — v2.9.10 Build 18

Build 18 source coverage was run with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -a -m pytest ... -p no:ddtrace` across the full `tests/test_*.py` suite in split chunks because the local single-process full run reached the container timeout before summary output.

Final source coverage result:

```text
TOTAL 5431 statements, 57 missed, 1766 branches, 42 partial branches, 99% coverage
```

Coverage gate status: PASS, TOTAL 99% preserved.

Post-unpack dev-source coverage is required by the Full Release Gate and is recorded separately in the post-unpack verification notes.
