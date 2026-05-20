# MVP COMPLIANCE MATRIX — script.oppo203.iso.external v2.0.0 Final

| MVP requirement | Status | Evidence |
|---|---|---|
| External Player MVP flow | Complete | Automated regression tests and post-unpack verification. |
| M9702 / Chinoppo wake rewrite | Complete | Model-gated tests preserve `#PON` / `#POW` to `#EJT`. |
| Stock OPPO behavior | Complete | Tests preserve stock `#PON` / `#POW` pass-through. |
| TCL / Android TV ADB switching | Complete for MVP | Tests cover TV-first ordering, disabled path, ADB command construction, non-fatal failure, and sentinel cleanup. |
| Session sentinel cleanup | Complete | Failure-path tests cover cleanup. |
| Fake OPPO server tests | Complete for MVP | Hermetic loopback tests cover OPPO responses and disconnect/reconnect behavior. |
| Kodi stubs foundation | Complete for MVP | Local stubs allow Kodi-bound imports in normal Python. |
| Release audit tooling | Complete | `tools/audit_release.py` is required for source and post-unpack verification. |
| Documentation lockstep | Complete for MVP | `README.md`, `reference.md`, and `web-references.md` updated for final release packaging. |
| Real hardware validation | Deferred | User will complete after the full merge; no hardware validation is claimed for this package. |
| 92% coverage gate | Deferred / post-MVP | Not a v2.0 MVP blocker. |
| Full v1.1.9 + v0.9.14 superset merge | Deferred / post-MVP | Reserved for later v2.1-style milestone. |
