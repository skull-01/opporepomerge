# Troubleshooting

## Base handoff fails

- Confirm the media type is eligible for external handoff.
- Confirm Kodi can read the library item.
- Confirm the player can reach the NAS/path that will be handed off or mapped.
- Test with TV switching disabled.
- Test with AVR sequencing disabled.

## TV switching fails

- Keep playback testing separate from TV control testing.
- Confirm the TV backend and command/preset values are correct.
- Review diagnostics for sanitized error details.
- Remember that TV control failure should be non-fatal.

## AVR sequencing fails

- Confirm AVR control is enabled intentionally.
- Confirm AVR power-off and volume automation are not enabled unless explicitly intended.
- Test query/dry-run actions before playback sequencing.
- Remember that AVR control failure should be non-fatal.

## Logs and privacy

Before sharing logs, remove:

- SmartThings tokens
- Sony PSKs
- passwords
- NAS credentials
- private network details you do not want public
