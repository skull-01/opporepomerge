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

## Configuration ownership

The Windows configurator (`configurator/`) is the single source of truth for the
add-on's persistent configuration — TV / OPPO / AVR / Kodi IPs,
`playercorefactory.xml`, the remote-bridge keymap, and hardware presets. The Kodi
add-on itself is **read-mostly**: it surfaces current values, accepts a small set of
in-the-moment overrides, and routes the user to the configurator for anything that
should persist across Kodi restarts.

**Allowed exceptions kept in the add-on:**

- Per-session toggles (e.g. verbose mode for a single playback test).
- The minimal in-add-on settings menu (TV / OPPO / AVR / Kodi IPs viewer plus
  language) — tracked by [issue #42](https://github.com/skull-01/script.oppo203.iso.external/issues/42).
- Diagnostic exports already exposed in the installer menu (AVR readiness, file-list
  diagnostic, discovery probe).

**Not in scope for the add-on** without an issue and operator sign-off:

- New persistent-setting categories in `resources/settings.xml`.
- New first-run or setup dialogs.
- Add-on side writers for `playercorefactory.xml`, the remote-bridge keymap, or NAS
  credentials.

Pull requests that introduce add-on-side configuration outside an allowed exception
will be redirected to the configurator.

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
python tools/audit_release.py --expected-version 2.9.16
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
