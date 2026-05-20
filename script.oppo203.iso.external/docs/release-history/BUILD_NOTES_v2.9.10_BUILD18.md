# Build Notes — v2.9.10 Build 18

Build 18 is the Full Release Gate regression, audit, and packaging candidate after v2.9.10 Build 17 unified TV + AVR playback sequencing.

## Scope

- Refresh active build identity to v2.9.10 Build 18.
- Add regression/audit candidate evidence and manifest entries.
- Preserve Build 17 unified TV + AVR sequencing behavior.
- Package the runtime ZIP, dev-source ZIP, artifact bundle, and SHA256 checksum.
- Do not add new hardware features.

## Preserved behavior

- AVR sequencing runs only for eligible OPPO/external-player handoff.
- AVR disabled path is a no-op.
- AVR and TV failures do not block playback.
- Optional AVR restore runs only if enabled.
- Existing TV restore continues to work.
- Startup power, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, OPPO command-map payloads, runtime ZIP policy, and 99% coverage gate remain preserved.

## Hardware validation

Hardware validation was not performed and is not claimed.
