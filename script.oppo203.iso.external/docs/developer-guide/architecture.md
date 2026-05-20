# Developer Guide — Architecture

## Purpose

`script.oppo203.iso.external` is a Kodi add-on that routes eligible disc-style and 4K UHD media to an external OPPO UDP-203/UDP-205-compatible playback workflow while preserving Kodi as the browsing and launch surface.

This document is for maintainers and AI coding agents. It explains the main runtime boundaries without changing the protected v2.9.10 Final behavior.

## Runtime entry points

| File | Role |
|---|---|
| `default.py` | Kodi plugin/add-on entry point for user-triggered actions. |
| `service.py` | Kodi service entry point for startup checks, interception, diagnostics, and background behavior. |
| `resources/lib/` | Main implementation modules. |
| `resources/settings.xml` | Kodi settings schema exposed to users. |
| `addon.xml` | Kodi add-on manifest and version identity. |

## Main functional areas

### Service interception

The service layer observes Kodi playback activity and determines whether a media item should remain inside Kodi or be handed off to the external-player path. The interception path must stay conservative: media that is not clearly eligible should not be forced into the OPPO/external route.

Protected behavior:

- Service interception must not break normal Kodi playback.
- Loose/raw file exclusion must remain intact.
- Unsupported or ambiguous paths should fail safe.

### External-player routing

External-player routing decides whether an item is eligible for OPPO/external playback. It coordinates path classification, player capability gates, playercorefactory configuration, NAS/AutoScript handling, and optional TV/AVR sequencing.

Protected behavior:

- OPPO playback routing must remain stable.
- 4K/UHD disc-style handoff behavior must not be changed casually.
- Non-eligible media must not be redirected unexpectedly.

### Player taxonomy and capability gates

The project contains hardware/player taxonomy logic so different player classes can be described without hard-coding every behavior into one branch. Capability gates are used to prevent unsupported actions from running on unsupported hardware profiles.

Maintainer rule:

- Add new player support through capability declarations and tests, not by weakening existing eligibility checks.

### OPPO command map

OPPO control is intentionally externalized through command-map payloads. This allows the command vocabulary and supported control operations to be tested independently from high-level routing.

Maintainer rule:

- Do not change OPPO command payloads without targeted tests.
- Preserve command-map audit behavior.

### TV control

TV control is optional sequencing around playback handoff. It may include vendor-specific backends and request helpers.

Protected behavior:

- TV control failures must not block playback.
- TV restore must continue to work when configured.
- Credentials and sensitive tokens must not be logged.

### AVR sequencing

AVR sequencing is optional and must only run for eligible OPPO/external-player handoff.

Protected behavior:

- Disabled AVR path is a no-op.
- AVR failures do not block playback.
- Optional AVR restore only runs when enabled.
- Volume/power automation must remain conservative and disabled unless configured.

### NAS and AutoScript behavior

NAS/AutoScript support bridges Kodi paths and OPPO-compatible playback workflows. This area is sensitive because network paths, SMB/NFS mounts, and OPPO behavior may differ between users.

Protected behavior:

- NAS path mapping must remain explicit and test-backed.
- AutoScript behavior must not be modified without reconstruction notes and tests.

### Playercorefactory generation and merge

The add-on can generate or merge `playercorefactory.xml` entries to support external-player launching. This must remain safe for users with existing Kodi playercorefactory customizations.

Protected behavior:

- Preserve merge safety.
- Preserve backup/restore semantics.
- Avoid overwriting user customizations unexpectedly.

### Settings and wizard flow

Kodi settings are defined in `resources/settings.xml`. The wizard is the user-facing path for safe setup and recovery.

Maintainer rule:

- Settings keys are compatibility contracts. Do not rename or remove them without migration tests.
- Wizard recovery/cancel/retry behavior must remain safe.

### Diagnostics and logging

Diagnostics must help users report issues without leaking secrets.

Maintainer rules:

- Never log SmartThings tokens.
- Never log Sony PSKs.
- Never expose passwords, tokens, or local credential material in diagnostic exports.
- Keep diagnostic summaries concise and actionable.

## Packaging boundaries

Runtime ZIP must contain only installable Kodi runtime files.

Allowed runtime areas include:

- `addon.xml`
- `default.py`
- `service.py`
- `resources/`
- required runtime metadata/media/language files

Forbidden runtime ZIP content:

- `tests/`
- `tools/`
- `scripts/`
- `docs/`
- `release-evidence/`
- GitHub readiness reports
- AI handoff files
- coverage/audit reports

## Development rule

For GitHub readiness builds G0-G8, runtime behavior must remain unchanged. Any future logic refactor should be a separate, narrow, test-backed build.
