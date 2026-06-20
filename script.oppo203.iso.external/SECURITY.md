# Security Policy

## Supported version

The current software-verified line is `v2.9.10 Final` and its GitHub-readiness builds. Older historical builds are preserved for reconstruction but are not the preferred target for new reports.

## Reporting a vulnerability

Please report security issues privately to the maintainer before publishing details. Include:

- Add-on version
- Kodi version and platform
- Affected module or workflow
- Steps to reproduce
- Expected and actual result
- Sanitized logs

Do not include private credentials, tokens, Sony PSKs, SmartThings tokens, NAS passwords, or private network secrets in public issues.

## Security expectations

The project should continue to follow these rules:

- Never log or export SmartThings tokens.
- Never log or export Sony PSKs.
- Never export credentials in diagnostics.
- Avoid `shell=True` for subprocess use.
- Use bounded timeouts for network calls.
- Avoid infinite retry loops.
- Treat optional TV/AVR failures as non-fatal.
- Keep AVR volume automation and AVR power-off disabled by default.
- Keep hardware-validation claims separate from software support.
