# Build Notes — v2.2.0 Build 10

Build 10 is a merge-compliance candidate checkpoint from Build 9. It adds a formal `MERGE_COMPLIANCE_MATRIX_v2.2.0_BUILD10.md` and implements the improved verification workflow discovered after Build 9: commands are run one at a time, and coverage uses `-p no:ddtrace` to avoid local container timeout behavior.

Build 10 does not declare the v1.1.9 + v0.9.14 superset merge complete. The matrix records remaining wizard/UI reconciliation and real hardware validation as open items.

## Scope

- Merge-compliance matrix and audit evidence.
- Self-contained AI handoff continuation requirement preserved.
- 99 percent coverage gate preserved.
- No broad merge or runtime feature expansion.

## Baseline

`script.oppo203.iso.external-2.2.0-build9.zip`
