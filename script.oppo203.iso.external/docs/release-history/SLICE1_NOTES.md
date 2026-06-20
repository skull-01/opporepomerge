# v2.0 Slice 1 Notes - Build 1

Build 1 establishes the v2.0 MVP identity from the verified v1.x baseline.

Implemented in this build:

- `addon.xml` version set to `2.0.0`.
- Add-on metadata updated to describe the MVP-first release line.
- Hardware model setting exposed for OPPO/Chinoppo selection.
- Older architecture-selection settings removed from the visible Kodi settings UI. Internal defaults remain so existing code paths do not break during the MVP transition.
- Documentation updated in `README.md`, `reference.md`, and `web-references.md`.

Deferred:

- Full cleanup of historical architecture documentation.
- Complete Slice 3 TCL/Android TV hardening.
- Fake OPPO server integration tests.
