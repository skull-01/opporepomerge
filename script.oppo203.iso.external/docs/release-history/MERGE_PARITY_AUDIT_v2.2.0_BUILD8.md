# Merge Parity Audit — v2.2.0 Build 8

```yaml
build: v2.2.0 Build 8
addon_version: 2.2.0.8
baseline: script.oppo203.iso.external-2.2.0-build7.zip
scope: narrow v1.1.9 + v0.9.14 superset-merge parity checkpoint
full_merge_status: in_progress_not_complete
coverage_gate: 99 percent enforced
```

## Purpose

Build 8 is a checkpoint build. It does not broaden runtime feature scope. It records what has already been ported from the v0.9.14 hardware-compatibility line into the v2.2 gradual merge line and makes the next handoff self-contained by requiring reconstruction data for the latest build.

## Completed merge slices through Build 8

| Area | Status | Evidence |
|---|---|---|
| Chinoppo/M9702 wake rewrite | Complete in current line | Existing wake-rewrite tests and command-map audit remain passing. |
| Stock OPPO pass-through | Complete in current line | Existing stock OPPO tests remain passing. |
| Reavon warning-only behavior | Complete for current line | Build 2–6 tests cover warning-only behavior and no command-map mutation. |
| M9203/M9205C hardware assertions | Complete for current line | Build 2 tests lock targeted clone profile and preset behavior. |
| AutoScript verbose-push warning helper | Complete for current line | Build 2–6 tests cover collection, logging, and UI surfacing. |
| Quick Start warning helper | Complete for current line | Build 2–6 tests cover collection and surfacing. |
| Service `onSettingsChanged()` watcher | Partially complete | Builds 1, 3, 4, and 7 cover model, jailbreak, AutoScript, warning logging, and persistence edge cases. |
| Active wizard warning surfacing | Partially complete | Builds 5–6 add and wire one warning-surfacing path without replacing the v1.x wizard. |
| Full v1.1.9 + v0.9.14 wizard union | Not complete | Deferred for later slices; active v1.x wizard remains in place. |
| Full v0.9.14 test parity | In progress | Build 8 marks this audit checkpoint; remaining tests should be ported only when they protect unique behavior not already covered. |

## Remaining before merge-complete candidate

```text
[ ] Audit remaining v0.9.14 tests against the current v2.2 test suite.
[ ] Port only unique tests that protect behavior not already covered.
[ ] Reconcile remaining wizard/UI flows without replacing stable v1.x behavior in one large step.
[ ] Reconcile remaining service watcher edge cases.
[ ] Produce a merge-compliance matrix when the union is believed complete.
[ ] Package a merge-complete candidate only after tests, coverage, audit, and post-unpack verification pass.
```

## Build 8 non-goals

```text
[not done] broad/full merge
[not done] real hardware validation
[not done] Reavon command-map support
[not done] removal of historical reconstruction data
[not done] lowering the 99 percent coverage gate
```
