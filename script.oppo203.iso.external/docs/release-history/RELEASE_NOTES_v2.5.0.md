# Release Notes — v2.5.0 Final

Version 2.5.0 is the v2.5 stability, wizard-recovery, and diagnostics release built on top of the v2.2.0 software-merge baseline.

## Highlights

- Stability-first configuration and settings helper improvements.
- Safer recovery from corrupt or partially written settings files.
- Clearer wizard messages without changing wizard branch order.
- Wizard recovery metadata for cancel/retry/partial setup support.
- Standardized diagnostic log prefixes.
- Lightweight diagnostic summary helper for support use.
- Combined regression and final packaging verification.

## Hardware validation

Hardware validation was skipped before final packaging at the user's request and is deferred to post-final user testing.

## Compatibility

The release preserves v2.2.0/v2.5 Build 7 runtime behavior, including OPPO command behavior, TV switching behavior, HTTP payload behavior, hardware presets, Reavon warning-only behavior, Chinoppo wake rewrite behavior, service interception behavior, and persisted setting semantics.
