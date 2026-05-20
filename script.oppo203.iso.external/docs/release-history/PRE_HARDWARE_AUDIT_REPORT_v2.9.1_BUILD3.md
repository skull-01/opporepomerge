# Pre-Hardware Audit Report — v2.9.1 Build 3

Build 3 is intended to preserve runtime behavior while externalizing command-map data. Before hardware testing, confirm that:

- The command map has 76 keys.
- No `#SIS`, `#PGU`, or `#PGD` tokens are present.
- Stock OPPO power commands still pass through.
- Chinoppo/M9702 wake rewrite behavior remains preserved.
- Reavon behavior remains warning-only.
- Runtime ZIP remains runtime-only.

Hardware validation is not claimed by this automated build.
