# Build Notes — v2.9.10 Build 10

Build 10 adds the TV diagnostics and dry-run validator slice. It introduces `resources/lib/tv_diagnostics.py` for selected TV backend validation, network-free dry-run reports for OPPO/Kodi target switching, explicit non-fatal test-action helpers, and sanitized diagnostic report export.

The build does not launch ISO playback, change OPPO routing, change `playercorefactory.xml`, alter NAS/AutoScript behavior, modify OPPO command-map payloads, or claim hardware validation.

## Key safeguards

- Dry-run reporting performs no ADB, Roku ECP, Sony Bravia, SmartThings, shell, or network calls.
- SmartThings tokens, Sony PSKs, passwords, credentials, secrets, and command output fields are redacted from reports.
- Reports explicitly include `hardware_validation_claimed=false`.
- Explicit switch test helpers are separate from dry-run diagnostics and return non-fatal sanitized results.
- SmartThings 9A/9B acknowledgement and token-redaction guardrails remain preserved.
