# Roadmap — v2.5 Development Series

The v2.5 series is the active development cycle after the v2.2.0 software-merge baseline. v2.2.0 is treated as merge-complete unless hardware validation reveals a specific defect.

## Active priorities

1. Stability-first enhancement.
2. User experience and wizard refinement.
3. Diagnostics and supportability.

## Stability-first enhancement

- Preserve all v2.2.0 verified behavior.
- Prefer additive guardrails over rewrites.
- Add regression tests for bug fixes when practical.
- Treat playback, ISO mounting, OPPO command maps, wake behavior, Reavon handling, and service watcher changes as high-risk.

## User experience and wizard refinement

- Improve setup wording and compatibility warnings.
- Keep warnings specific, actionable, and non-alarming.
- Preserve working wizard flows.
- Test fresh install, upgrade, cancel, retry, invalid path, missing external player, and partial setup flows when wizard logic changes.

## Diagnostics and supportability

- Standardize useful log categories without adding noise.
- Distinguish configuration, path, player, ISO, mount, wizard-cancelled, and internal errors.
- Avoid misleading success messages after partial failures.
- Add support-friendly troubleshooting notes as hardware validation results are received.

## Build strategy

- Build 1: v2.5 baseline, documentation, trackers, versioning, packaging.
- Build 2: stability guardrails around settings, paths, and retry states.
- Build 3: wizard message cleanup without behavior changes.
- Build 4: wizard cancel/retry/partial-setup recovery improvements.
- Build 5: diagnostic logging standardization.
- Build 6: lightweight diagnostic summary helper.
- Build 7: combined regression and packaging candidate.
