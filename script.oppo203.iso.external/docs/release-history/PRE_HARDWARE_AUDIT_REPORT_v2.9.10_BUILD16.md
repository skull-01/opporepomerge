# v2.9.10 Build 16 — AVR wizard, diagnostics, and safety UI

v2.9.10 Build 16 adds AVR setup UI helpers, query-only AVR test actions, explicit user-action gates for power/input tests, sanitized AVR diagnostic export, and safety wording. AVR support remains disabled by default, AVR power-off and volume automation remain disabled by default, no AVR playback sequencing hook is added, diagnostics sanitize credentials and state hardware_validation_claimed=false, and hardware validation is not claimed.

## Pre-hardware posture

Software-only readiness remains in place. Diagnostic exports sanitize credentials and report `hardware_validation_claimed=false`.
