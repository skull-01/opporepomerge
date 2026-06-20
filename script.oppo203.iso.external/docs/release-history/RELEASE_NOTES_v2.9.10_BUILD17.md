# Release Notes — v2.9.10 Build 17

Build 17 safely hooks optional TV and AVR pre/post sequencing into the external-player flow. AVR sequencing runs only for eligible OPPO/external-player handoff, the AVR disabled path is a no-op, TV and AVR failures remain non-fatal, optional AVR restore runs only when enabled, and existing TV restore continues to work.

No real hardware validation was performed or claimed.
