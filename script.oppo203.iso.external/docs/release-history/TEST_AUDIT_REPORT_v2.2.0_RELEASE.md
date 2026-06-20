# Test and Audit Report — v2.2.0 Release

This file records the dedicated v2.2.0 packaging build verification. Exact source and post-unpack results are recorded in the final response and v27 handoff after execution.

Required commands:

```bash
python -m pytest -q -p no:ddtrace
python -m unittest discover -s tests -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m coverage run -m pytest -q -p no:ddtrace
python -m coverage report -m
python tools/audit_release.py --expected-version 2.2.0
```
