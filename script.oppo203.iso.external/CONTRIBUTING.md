# Contributing

Thank you for helping improve `script.oppo203.iso.external`.

This project is intentionally conservative because it controls external playback, optional TV input switching, optional AVR sequencing, and home-theater automation paths. Small, test-backed changes are preferred.

## Ground rules

- Keep pull requests narrow and easy to review.
- Do not change playback routing, OPPO command payloads, TV switching, AVR sequencing, NAS/AutoScript behavior, or `playercorefactory.xml` behavior unless the pull request explicitly states the reason and adds regression tests.
- Do not claim real hardware validation unless a real tester report is included.
- Keep runtime ZIP contents clean. Tests, tools, docs, release evidence, handoff files, and reports must not be included in the installable Kodi ZIP.
- Update documentation when behavior, setup steps, warnings, or validation status changes.
- Preserve the AI handoff and historical reconstruction discipline for build-style work.

## Local checks

Run the practical checks before opening a pull request:

```bash
python -m py_compile service.py default.py
python tools/render_docs.py --check
python tools/sync_version.py --check
python tools/test_layout.py --check
python tools/i18n_extract.py --check
pytest -q tests/test_v2910_final_release.py
pytest -q tests/test_v2910*.py
python tools/audit_release.py --expected-version 2.9.10
```

For release or packaging work, also run the full pytest/unittest/coverage gates, packaging script, runtime ZIP audit, and post-unpack dev-source verification.

## Hardware reports

Hardware reports should include:

- Add-on version and build identity
- Kodi version and platform
- Player model and firmware
- Connection method
- TV/AVR model if relevant
- Media type and path style
- Exact expected result and actual result
- Sanitized logs or screenshots where possible

Do not include passwords, tokens, Sony PSKs, SmartThings tokens, private NAS credentials, or personally sensitive network details.

## AI maintainer note

When an AI agent performs a build, it must produce build notes, manifest, test audit, hardware-validation status, AI handoff, historical reconstruction entry, and artifact bundle. It must also record any validation limitations honestly.
