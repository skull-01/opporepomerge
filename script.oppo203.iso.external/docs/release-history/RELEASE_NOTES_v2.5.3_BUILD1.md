# Release Notes — v2.5.3 Build 1

v2.5.3 Build 1 adds the software classifier for 4K UHD disc-style interception and wires service interception to that classifier.

## Added

- Tagged 4K/UHD/2160p disc-style classifier.
- Service-interception gate that uses the new classifier.
- Loose/raw video exclusion list so Kodi remains the default player for normal files.
- Targeted tests for the approved trigger behavior.

## Preserved

- Existing OPPO/Chinoppo command behavior.
- Startup power-on behavior from v2.5.1/v2.5.2.
- NAS capability and dry-run planning work from v2.5.2.
- Historical intercept.py APIs used by existing tests and callers.

## Deferred

- playercorefactory.xml Option 4 conservative tag-aware rule generation.
- Wizard launch naming-convention warning.
- Final packaging/audit build.

## Hardware validation

No hardware validation is claimed. This build is ready for software review only.

