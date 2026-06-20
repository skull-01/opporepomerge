# Build Notes — v2.5.2 Build 2

## Purpose

v2.5.2 Build 2 optimizes the installable Kodi ZIP so it contains only runtime add-on files. It preserves v2.5.2 Build 1 OPPO/Chinoppo NAS playback capability gates and the v2.5.1 startup-power fix.

## Planned success rate

90%.

The scope is packaging and handoff cleanup only, with no path-mapping, NAS playback trigger, wizard NAS setup, or AutoScript runtime behavior changes.

## Completed scope

- Added a runtime-focused packaging helper.
- Excluded build notes, coverage reports, hardware-validation records, merge/MVP compliance matrices, release manifests, release notes, roadmaps, slice notes, test-audit reports, tests, tools, CI files, and other development-only files from the installable ZIP.
- Preserved evidence in the source tree, artifact bundle, and combined AI handoff Markdown.
- Updated add-on metadata to identify Build 2 as a package-optimization build.
- Added tests that verify runtime files are included and development/evidence files are excluded.
- Added a mandatory future-build rule: installable ZIPs must remain runtime-focused and evidence must be preserved in the handoff/artifact bundle.

## Runtime behavior

No runtime behavior changed. OPPO/Chinoppo NAS playback capability gates from Build 1 are preserved, and active NAS path mapping/playback trigger work remains deferred to the next development build.

## Hardware validation

No new hardware validation was performed. User-confirmed NAS-mounted playback remains recorded as a capability finding, but per-model tester validation remains pending.
