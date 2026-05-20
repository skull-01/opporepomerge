# Coverage Report — v2.2.0 Build 10

The coverage gate remains enforced at 99 percent.

Verification command:

```bash
python -m coverage run -m pytest -q -p no:ddtrace
python -m coverage report -m
```

Observed source result:

```text
TOTAL 99%
```

Raw coverage report tail:

```text
resources/lib/settings_reader.py             136      6     58      3    95%   111, 188-189, 195-196, 201->199, 214
resources/lib/tv_control.py                   55      0     18      0   100%
resources/lib/wizard.py                      204     10     52      2    95%   51, 54-57, 60, 69, 72, 77->exit, 79-80, 260->262
resources/lib/wizard_polish.py                67      0     18      0   100%
--------------------------------------------------------------------------------------
TOTAL                                       2760     25    982     18    99%
```
