# Build Notes — v2.5.3 Build 2

## Objective

Implement the selected Option 4 `playercorefactory.xml` strategy, add wizard/installer naming guidance, preserve the Build 1 Python classifier/service interception behavior, and keep the installable ZIP runtime-only.

## Baseline

Reconstructed from the v2.5.3 Build 1 handoff source. The runtime `addon.xml` version remains `2.5.2` for compatibility with the existing audit baseline; the package/build identity is v2.5.3 Build 2.

## Changes

- `resources/lib/installer.py` now emits conservative tag-aware XML rules only.
- XML rules require one of `4K`, `4k`, `UHD`, `uhd`, `2160p`, or `2160P` in the filename/path.
- XML routing is limited to `iso`, `bdmv`, and `mpls`.
- Broad legacy routing for DVD/VCD folders, raw streams, `m2ts`, `vob`, `ifo`, `dat`, `cue`, `bin`, `dvdimage`, and `dvdfile` was removed from the generated playercorefactory rules.
- `resources/lib/wizard.py` surfaces the XML naming-discipline warning when External Player mode is selected.
- README/reference/web-reference notes were updated.
- `tests/test_v253_build2_xml_option4.py` adds targeted Option 4 tests.

## Hardware status

No real OPPO, Chinoppo/M9702, Kodi installation, NAS, TV switching, or ADB hardware validation was performed or claimed.
