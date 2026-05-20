# Build Notes — v2.5.0 Build 6

## Planned success rate

80% — lightweight diagnostic summary helper only.

## Scope

Build 6 adds a non-invasive diagnostic summary helper for support and AI handoff triage. The helper reports add-on version, setup completeness, key configuration status, missing required settings, selected warnings, and safe path/dependency status.

## Files changed

- `resources/lib/diagnostic_summary.py` added.
- `tests/test_v250_build6_diagnostic_summary.py` added.
- `tools/audit_release.py` updated to require Build 6 evidence files.

## Behavior preservation

No playback flow, wizard branch order, OPPO command behavior, TV switching behavior, HTTP payload behavior, hardware preset behavior, service interception behavior, or persisted setting semantics were intentionally changed.

## Notes

The diagnostic summary helper is read-only. It can inspect supplied settings, optionally read `settings.xml` through the existing tolerant settings reader, and optionally check configured path-like dependencies. It does not launch players, contact hardware, mutate settings, or require Kodi modules.
