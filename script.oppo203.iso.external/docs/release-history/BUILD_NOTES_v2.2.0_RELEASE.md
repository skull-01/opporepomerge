# Build Notes — v2.2.0 Release Packaging

Version: 2.2.0
Baseline: v2.2.0 Build 12 (`2.2.0.12`)
Role: dedicated release-candidate/final packaging build from the software merge-complete candidate line.

## Summary

This packaging build converts the verified Build 12 software merge-complete candidate into a clean v2.2.0 release package. Real hardware validation remains explicitly deferred to the user after packaging. No runtime feature expansion was performed.

## Build-process improvements preserved

- Verification commands are run one at a time.
- Coverage verification uses `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and `-p no:ddtrace` to avoid the local ddtrace timeout behavior.
- Post-unpack verification remains a separate release-blocking phase.
- The AI handoff remains self-contained with a full latest-build reconstruction bundle.

## Hardware validation status

Not performed in this automated packaging build. The user will perform real OPPO / Chinoppo / TCL / Android TV / ADB hardware validation after packaging.
