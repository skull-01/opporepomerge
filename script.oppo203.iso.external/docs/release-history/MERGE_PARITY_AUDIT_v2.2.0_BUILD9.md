# Merge Parity Audit — v2.2.0 Build 9

```yaml
build: v2.2.0 Build 9
addon_version: 2.2.0.9
baseline: script.oppo203.iso.external-2.2.0-build8.zip
scope: narrow v1.1.9 + v0.9.14 test-parity audit slice
full_merge_status: in_progress_not_complete
coverage_gate: 99 percent enforced
```

## Purpose

Build 9 is a test-parity audit checkpoint.  It does not broaden runtime feature scope.  It records which v0.9.14 hardware-compatibility behaviors are already protected in the v2.2 merge line and identifies the remaining work before a merge-complete candidate.

## Behavior already protected by tests in the v2.2 line

| Behavior | Status | Evidence |
|---|---|---|
| Chinoppo/M9702 `#PON/#POW -> #EJT` rewrite | Protected | Existing wake-rewrite tests and command-map invariants remain passing. |
| Stock OPPO `#PON/#POW` pass-through | Protected | Stock OPPO pass-through tests remain passing. |
| Reavon warning-only behavior | Protected | Build 2 through Build 7 tests cover warnings and no command-map mutation. |
| M9203/M9205C clone profiles | Protected | Build 2 tests cover profile and preset behavior. |
| Jailbroken stock OPPO JSON payload mode | Protected | Build 2 and Build 7 tests cover `oppo_http_payload_mode=json_payload` persistence. |
| AutoScript verbose-push warning | Protected | Build 2, 3, 5, and 6 tests cover helper, logging, and UI surfacing. |
| Quick Start warning helper | Protected | Build 2, 3, 5, and 6 tests cover collection and surfacing. |
| Service `onSettingsChanged()` watcher | Partially protected | Builds 1, 3, 4, 6, and 7 cover model/jailbreak/AutoScript deltas and persistence edge cases. |
| Active wizard warning surfacing | Partially protected | Builds 5 and 6 wire one active path without replacing the stable v1.x wizard. |
| Self-contained handoff reconstruction | Protected | Build 8 handoff embeds latest source reconstruction; Build 9 preserves this as a mandatory future-build rule. |

## Remaining merge areas before a merge-complete candidate

```text
[ ] Perform one more pass for service watcher edge cases around repeated changes and save failure resilience.
[ ] Reconcile remaining wizard/UI flows without replacing the stable v1.x wizard in one large step.
[ ] Produce a merge-compliance matrix when the union is believed complete.
[ ] Run a final full merge-compliance audit against the v0.9.14 inventory and v1.1.9 inventory.
[ ] Package a merge-complete candidate only after source and post-unpack verification pass.
```

## Build 9 non-goals

```text
[not done] broad/full merge
[not done] real hardware validation
[not done] Reavon command-map support
[not done] lowering the 99 percent coverage gate
[not done] deleting historical reconstruction data
```
