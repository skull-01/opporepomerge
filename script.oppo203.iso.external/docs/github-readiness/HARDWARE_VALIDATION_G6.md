# Hardware Validation — GitHub Readiness Build G6

## Status

Hardware validation was not performed and is not claimed.

## Build scope

G6 is a GitHub CI hardening build. It adds or updates:

- GitHub Actions workflow
- Dependabot configuration
- CI documentation
- CI configuration tests
- `scripts/verify.sh` expected-version default

## Runtime behavior

Runtime behavior changed: false.

G6 does not change:

- OPPO playback routing
- OPPO command-map payloads
- TV control
- AVR sequencing
- NAS / AutoScript behavior
- service interception
- `playercorefactory.xml` behavior
- startup power behavior
- settings behavior

## Claim rule

Do not change this status from `not performed / not claimed` unless real tester evidence is supplied for the relevant hardware path.
