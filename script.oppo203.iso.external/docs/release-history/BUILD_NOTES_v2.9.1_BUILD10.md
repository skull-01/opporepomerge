# Build Notes — v2.9.1 Build 10

## Scope

Build 10 refactors `tools/audit_release.py` so audit collection and reporting are separate concerns. It adds a typed `AuditCheck` value object plus `TextReporter` and `JsonReporter` classes while preserving the legacy `run_audit()` list-of-dicts API and the existing text/JSON CLI schemas.

## Behavior

No runtime playback, OPPO command, XML routing, NAS, settings fallback, startup auto-power, or hardware-control behavior changed.

## Protected invariants

- Canonical 76-key OPPO command map remains enforced.
- Forbidden tokens `#SIS`, `#PGU`, and `#PGD` remain blocked.
- 99% coverage gate remains enforced.
- Runtime ZIP remains allowlist-driven and excludes tests/tools/scripts/evidence/handoff files.
- Hardware validation is not performed and not claimed.
