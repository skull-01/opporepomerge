# Coverage Report — v2.1.0 Build 5

```text
python -m coverage run -m pytest -q
413 passed

python -m coverage report -m
TOTAL 98%
```

The enforced coverage gate is now:

```ini
fail_under = 98
```

This is a gradual pre-merge hardening step. The final 99% target remains pending.
