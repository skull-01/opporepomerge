# Configurator v0.9.4 — build notes

**Released:** 2026-06-03 · **tag:** `configurator-v0.9.4`
**Built + published by:** GitHub Actions (`.github/workflows/configurator-ci.yml` → `release` job) on the tag push.
**Bundles add-on:** v2.9.15 — now also carrying the add-on robustness fixes below (the CI `bundle:addon`
step repackages `main`'s add-on source through the build-tag packaging tool).

## What shipped

A quality + capability roll-up on top of v0.9.3 — the "review → property-test → AVR raw console" pass.

### 1. Dev-console hardening (review fixes) — [#328](https://github.com/skull-01/script.oppo203.iso.external/pull/328)

An independent adversarial review of the session's ~21 PRs found **no high/blocking issues**; this applied its medium + low hardening findings:

- `nas_test_smb` rejects `net use` credentials that net.exe would re-tokenize (quotes/newlines, or a `/`-leading / `*` password it reads as a switch or interactive prompt).
- `autoscript_push_telnet` rejects a script line equal to the heredoc terminator (`OPPOEOF`).
- `validate_addon_zip` caps each zip entry's decompressed read at 16 MB.
- `install_addon_zip` rejects quotes/newlines in the addons path.
- Honesty relabel: the Kodi panel says **"build tag verified"** (not "signed build") — it is a content-integrity tag, not a cryptographic signature.

### 2. Add-on property-test pass — [#329](https://github.com/skull-01/script.oppo203.iso.external/issues/329) / [#330](https://github.com/skull-01/script.oppo203.iso.external/pull/330) (area:addon)

A property/fuzz sweep over the add-on's pure helpers fixed a cluster of `int()`-coercion crashes (same root cause an earlier play-status pass fixed in `oppo_control`/`i18n`): a textual (`"8060/tcp"`) or non-finite (`inf`) port from device-cache JSON / an mDNS record / a JSON AutoScript preset previously raised instead of degrading.

- `oppo/discovery.py` — new `_safe_port()` routed through `parse_mdns_record`, `DeviceCache.add`, `DeviceCache.load`.
- `oppo/autoscript_helper.py` — `_safe_int()` now catches `OverflowError`.
- `tests/test_property_addon_robustness.py` pins the four fixes plus the eISCP frame round-trip and path-normalize idempotence (optional Hypothesis + curated deterministic fallback so the gate never weakens). These ride into the bundled add-on.

### 3. AVR raw-command console — [#331](https://github.com/skull-01/script.oppo203.iso.external/issues/331) / [#332](https://github.com/skull-01/script.oppo203.iso.external/pull/332)

The dev panel's AV receiver tab gains a raw-command console (arbitrary power/volume/mute/query) alongside input-select, fired through a new thin Rust `avr_raw_send`:

- **Denon/Marantz** line-ASCII over telnet (`:23`, CR-appended); **Onkyo/Pioneer** eISCP payload framed over `:60128`; **Yamaha** MusicCast API path over HTTP (`:80`). **Sony** keeps its `setPlayContent` URI box (its API has no line protocol).
- Pure builders (`denon_raw_command` / `eiscp_raw_payload` / `yamaha_raw_path`) reject control chars, over-length input, and non-absolute / traversal / header-splitting paths before any socket opens. Each backend gets a preset palette + a free-form box on the shared transcript. Best-effort + hardware-pending.

## Gates (software-verified only)

- Configurator: `tsc -b` clean · **vitest 356** (incl. `version.test.ts` version-consistency) · **`cargo test` 57** · `vite build`.
- Add-on (#330, bundled): `pytest -n auto` **1187 passed / 3 skipped** · serial coverage **99%** (`coverage report` exit 0) · ruff check + format clean.
- **Cross-language guard** (from v0.9.3) still holds: the Python↔Rust build-tag manifest is pinned to one shared fixture hash.
- **Hardware validation NOT claimed.** The AVR raw commands against real receivers, and the add-on cache/mDNS recovery on-device, are Phase-C/operator — see [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](../../../docs/MANUAL_VERIFICATION_CHECKLIST.md).

## Artifacts + SHA-256

MSI + NSIS installers + `SHA256SUMS.txt` produced by the CI release job, attached to the published
release (**unsigned**). Verify against that file:

- https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.9.4
