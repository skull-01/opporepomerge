# Build Notes — v2.2.0 Release 2.2.0

```yaml
version: 2.2.0
artifact: script.oppo203.iso.external-2.2.0-build12.zip
baseline: script.oppo203.iso.external-2.2.0-build11.zip
focus: final merge-compliance review and release-candidate stabilization
```

Release 2.2.0 performs a final software merge-compliance review for the gradual v1.1.9 + v0.9.14 superset merge. It does not add broad features. It records that the known hermetically testable software merge gaps have been closed and that remaining blockers are external hardware validation and release-candidate/final packaging decisions.

## Build-process improvements retained

- Verification commands are run one at a time.
- Coverage verification uses `python -m coverage run -m pytest -q -p no:ddtrace` or `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` equivalent to avoid the local ddtrace timeout behavior.
- Post-unpack verification is treated as a separate required phase.
- The latest AI handoff remains self-contained and embeds the complete latest source reconstruction.

## Scope boundaries

- No broad wizard replacement.
- No Reavon command maps.
- No real hardware claim.
- No full final-release claim.
- No weakening of the 99% coverage gate.
