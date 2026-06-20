# Test and Audit Report — v2.2.0 Release 2.2.0

```yaml
version: 2.2.0
verification_style: one_command_at_a_time
coverage_timeout_mitigation: -p no:ddtrace
```

## Source verification commands

```bash
python -m pytest -q -p no:ddtrace
python -m unittest discover -s tests
python -m coverage run -m pytest -q -p no:ddtrace
python -m coverage report -m
python tools/audit_release.py --expected-version 2.2.0
```

## Post-unpack verification commands

```bash
python -m pytest -q -p no:ddtrace
python -m unittest discover -s tests
python -m coverage run -m pytest -q -p no:ddtrace
python -m coverage report -m
python tools/audit_release.py --expected-version 2.2.0
```

Results are recorded in the final assistant response and in the Release 2.2.0 handoff.
