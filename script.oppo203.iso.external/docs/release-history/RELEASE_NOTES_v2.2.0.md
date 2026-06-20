# Release Notes — v2.2.0

## Summary

v2.2.0 packages the software merge-complete candidate produced by the gradual v1.1.9 + v0.9.14 superset merge line. It preserves the v2.0 MVP behavior, the 99 percent enforced coverage gate, and the Build 10+ improved verification process.

## Status

- Software merge-complete candidate: yes.
- Real hardware validated by this AI session: no.
- Hardware validation plan: user will validate after packaging.

## Included merge outcomes

- 12-SKU hardware compatibility table.
- Chinoppo/M9201/M9203/M9205C/M9702 wake rewrite.
- Stock OPPO pass-through behavior.
- Reavon warning-only behavior, with no command-map mutation.
- Quick Start and AutoScript verbose-push warnings.
- Jailbreak JSON payload mode for stock OPPO.
- `service.Monitor.onSettingsChanged()` compatibility watcher and persistence behavior.
- Wizard/UI compatibility-warning surfacing.
- Fake OPPO server tests and clean-disconnect invariant.
- 76-key canonical command map with no `#SIS`, `#PGU`, or `#PGD`.
- Self-contained AI handoff reconstruction discipline.

## Known caveat

No physical OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested in this automated packaging build.
