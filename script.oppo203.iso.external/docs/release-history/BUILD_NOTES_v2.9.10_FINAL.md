# Build Notes — v2.9.10 Final

Final v2.9.10 is the software-verified release packaging build after v2.9.10 Build 18 regression/audit candidate.

## Scope

- Refresh active release identity to v2.9.10 Final.
- Package final runtime ZIP, dev-source ZIP, artifact bundle, and SHA256 checksum.
- Preserve Build 17 unified TV + AVR sequencing behavior.
- Preserve Build 18 Full Release Gate evidence as the regression/audit baseline.
- Do not add new hardware features.

## Preserved behavior

- AVR sequencing runs only for eligible OPPO/external-player handoff.
- AVR disabled path is a no-op.
- AVR and TV failures do not block playback.
- Optional AVR restore runs only if enabled.
- Existing TV restore continues to work.
- Startup power, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, OPPO command-map payloads, runtime ZIP policy, and 99% coverage gate remain preserved.

## Hardware validation

This is a software-verified release. Real hardware validation was not performed or claimed.
