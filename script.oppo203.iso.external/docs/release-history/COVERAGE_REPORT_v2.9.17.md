# Coverage Report — v2.9.17 Final

Source coverage result for the v2.9.17 release (`resources/lib`, with UI/glue modules measured):

```text
TOTAL 5922 statements, 16 missed, 1940 branches, 49 partial branches, 99% coverage
```

The enforced gate in `.coveragerc` and `pyproject.toml` is `fail_under = 99`. The serial `coverage run -m pytest` then `coverage report` gate passes; the new `resources/lib/oppo/dolby_vision.py` module is covered by `tests/test_dolby_vision_capability.py`, and the five new clone variants are exercised by `tests/test_clone_variants_split.py`. CI is the authoritative coverage runner.
