# Build Notes - v2.1.0 Build 3

addon_version: 2.1.0.3
artifact_name: script.oppo203.iso.external-2.1.0-build3.zip
baseline: script.oppo203.iso.external-2.1.0-build2.zip

## Purpose

Continue the gradual pre-merge path toward 99% coverage by raising the enforced gate from 94% to 96%.

## Scope

Coverage/stub hardening only. No full v1.1.9 + v0.9.14 merge work was started.

## Changes

- Added targeted tests for OPPO discovery, OPPO TCP client, settings parsing, TV-control failures, AutoScript, architecture benchmark, wizard polish, logging, preset manager, and playercorefactory merge behavior.
- Fixed `oppo_control.discover_oppo()` cleanup when top-level UDP socket creation fails.
- Raised `.coveragerc` to `fail_under = 96`.
- Updated README.md, reference.md, web-references.md, audit tooling, and handoff.

## Known caveats

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested.
