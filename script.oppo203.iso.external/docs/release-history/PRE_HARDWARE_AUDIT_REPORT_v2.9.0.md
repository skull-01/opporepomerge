# Pre-Hardware Audit Report — Version 2.9.0

```yaml
release: 2.9.0
baseline: v2.5.3 Build 6
runtime_behavior_changed: false
hardware_claim: none
```

## Audit posture

Version 2.9.0 is suitable as a software-verified release rebuild for user hardware testing, subject to the final source, post-unpack, and runtime package audit results.

## Preserved hardware-sensitive invariants

- Stock OPPO power-command pass-through.
- Chinoppo/M9702 wake rewrite behavior.
- Reavon warning-only behavior.
- Canonical OPPO command-map invariants.
- 4K UHD disc-style-only interception.
- Loose/raw video exclusion.
- Runtime-only installable ZIP packaging.
