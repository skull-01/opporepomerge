# Developer Guide — Code Quality

## Principle

Keep the add-on boring, explicit, and testable. Avoid clever abstractions in hardware-control code unless they reduce risk and are backed by tests.

## Maintainability goals

- Small functions with clear names.
- Explicit capability gates.
- No hidden hardware claims.
- Conservative network timeouts.
- No secret leakage in logs.
- Tests for every behavior change.
- Documentation updates for every public behavior change.

## Protected modules

Treat these as high-risk modules. Avoid changing them during documentation/tooling builds:

```text
service.py
default.py
resources/lib/external_player.py
resources/lib/oppo_control.py
resources/lib/oppo_tcp_client.py
resources/lib/command_map.py
resources/lib/intercept.py
resources/lib/nas_playback_adapter.py
resources/lib/playercorefactory_merge.py
resources/lib/avr_sequence.py
resources/lib/tv_control.py
```

## Safe cleanup examples

Allowed in GitHub-readiness builds if tests pass:

- Documentation additions.
- File organization.
- Comments clarifying existing behavior.
- Public project metadata.
- Test helper path updates caused by documentation moves.

Avoid during GitHub-readiness builds:

- Behavioral refactors.
- New device support.
- Network-control logic changes.
- Settings key renames.
- Wizard flow changes.
- Command payload changes.

## Logging rules

Never log:

- tokens
- passwords
- Sony PSKs
- SmartThings credentials
- private network secrets

## Error-handling rules

- TV/AVR failures must not block playback.
- Disabled optional paths must be no-ops.
- Hardware control must fail safely.
- User diagnostics must describe next steps without exposing secrets.

## Formatting and linting

Formatting/linting should be introduced gradually:

1. Add tool configuration.
2. Run check-only mode.
3. Fix low-risk issues.
4. Apply formatting in a separate build.
5. Verify tests and package audit after formatting.

## GitHub Readiness G5 tooling baseline

Build G5 adds `pyproject.toml` and `requirements-dev.txt` so contributors and CI can install and run the same development tools without changing Kodi runtime behavior.

The project intentionally keeps the older standalone configuration files for compatibility with existing tests and helper scripts:

```text
pytest.ini
ruff.toml
mypy.ini
.coveragerc
```

The `pyproject.toml` file centralizes future-facing tool settings for Black, Ruff, Coverage, and MyPy. During the GitHub-readiness phase, these tools should be introduced in check-only mode first. Formatting or lint fixes should happen in a separate build so code changes remain easy to review.

`requirements-dev.txt` is development-only. It must not be required by Kodi runtime users and must never be packaged into the installable runtime ZIP.


## GitHub Readiness G6 CI baseline

Build G6 adds CI hardening with `.github/workflows/ci.yml` and `.github/dependabot.yml`. CI should run the project gates before pull requests are merged, but it remains software validation only. Hardware validation still requires real tester evidence recorded in the hardware-validation documents.

## GitHub Readiness G7 safe cleanup baseline

Build G7 performs a narrow format-hygiene pass without applying broad Black or Ruff rewrites. The safe cleanup is limited to archived GitHub-readiness Markdown files that had trailing spaces. Runtime modules are not reformatted in this build.

Ruff and Black remain configured for CI and future contributor environments. In environments where those tools are unavailable, maintainers should record tool availability honestly and avoid claiming a lint/format pass.
