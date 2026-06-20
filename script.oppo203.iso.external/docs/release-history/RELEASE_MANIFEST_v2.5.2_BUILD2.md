# Release Manifest — v2.5.2 Build 2

```yaml
version: 2.5.2
build: v2.5.2 Build 2
role: installable ZIP optimization and AI-handoff evidence consolidation
installable_zip: script.oppo203.iso.external-2.5.2-build2.zip
artifact_bundle: script.oppo203.iso.external-2.5.2-build2-artifacts-bundle.zip
runtime_behavior_change: none
hardware_validation: pending per-device user/tester validation
```

## Installable ZIP policy

The installable ZIP is runtime-focused. It contains Kodi runtime files only: `addon.xml`, `default.py`, `service.py`, and `resources/**` plus optional visual/license assets if present.

The installable ZIP must not include development/evidence files such as build notes, coverage reports, hardware-validation files, compliance matrices, manifests, release notes, roadmaps, slice notes, test-audit reports, tests, tools, CI config, or local coverage/test configuration.

## Evidence location

Release/development evidence is preserved in the combined DevLog/handoff Markdown and artifact bundle.
