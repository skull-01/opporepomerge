# Pre-Hardware Audit Report — v2.9.10 Build 7

Build 7 is a software-only Roku TV ECP backend slice.

Pre-hardware checks:

- Roku ECP keys are allowlisted before URL construction.
- Default Roku ECP port is `8060`.
- HTTP method is POST.
- Request path is `/keypress/<key>`.
- TV switching failures remain non-fatal in the existing playback flow.
- Hardware validation is not claimed.
