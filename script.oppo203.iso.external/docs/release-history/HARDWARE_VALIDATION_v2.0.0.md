# HARDWARE VALIDATION — script.oppo203.iso.external v2.0.0 Final

## Status

No new physical hardware validation was performed for this final v2.0.0 package. Physical hardware testing was not performed during this release packaging step. Real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, and ADB hardware validation are not claimed.

## Release decision

The final v2.0.0 MVP release is packaged from the verified Build 6 line using automated tests, release audit checks, and post-unpack verification. The user stated that real hardware testing will be completed after the later full v1.1.9 + v0.9.14-style merge.

## Automated coverage standing in for release packaging

- External Player MVP behavior is covered by regression tests.
- M9702 / Chinoppo wake rewrite behavior is covered by tests.
- Stock OPPO pass-through behavior is covered by tests.
- TCL / Android TV ADB switching order and failure behavior are covered by tests.
- Fake OPPO server behavior is covered by hermetic loopback tests.
- Kodi imports are covered by local stubs.
- Release audit and post-unpack verification are required before packaging.

## Caveat

Passing automated tests and audits does not prove real hardware behavior. Hardware validation remains deferred and must not be represented as complete for this package.
