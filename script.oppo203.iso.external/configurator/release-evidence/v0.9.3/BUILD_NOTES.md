# Configurator v0.9.3 — build notes

**Released:** 2026-06-03 · **tag:** `configurator-v0.9.3` · **commit:** `6266aa7`
**Built + published by:** GitHub Actions (`.github/workflows/configurator-ci.yml` → `release` job) on the tag push.
**Bundles add-on:** v2.9.15 — **now build-tagged** (the CI `bundle:addon` step repackages it through the updated packaging tool).

## What shipped — embedded add-on build tag (umbrella #322)

The deferred follow-up to the v0.9.2 add-on validation: stamp our installable add-on zip with an
integrity **tag** the configurator verifies + prefers.

- **PR 1** (#325, area:addon) — `tools/package_installable_zip.py` stamps `resources/oppokodiaddon.sig` (addon id + version + a SHA-256 content manifest over the zip's files, via `compute_manifest_sig`). Kodi-inert metadata under the allowlisted `resources/` dir; no add-on runtime change; the allowlist invariant (`set(namelist) == names`) holds.
- **PR 2** (#326) — `validate_addon_zip` recomputes the manifest (Rust `addon_manifest_sig`, dep `sha2`) → **signed** (matches) / **unsigned** (no tag — older build, still uploadable + labeled) / **mismatch** (tampered → blocked). The Kodi panel shows the state.
- **bump** (#327) — 0.9.2 → 0.9.3.

It is an **integrity/build tag, not a cryptographic signature** (the project ships unsigned; the
formula lives in the open repo). It deters wrong/corrupt/modified zips, not a determined forger.

## Gates (software-verified only)

- Add-on (PR 1): `pytest -n auto` **1162/3** · **serial coverage 99%** · ruff clean.
- Configurator (PR 2): `tsc -b` · **vitest 356** · **`cargo test` 54** · `vite build`.
- **Cross-language guard:** `tests/test_addon_signature.py` (Python) and a cargo test both pin `compute_manifest_sig`/`addon_manifest_sig` to the **same fixture hash** (`bbcc6382…`), so the packaging↔validation manifest cannot silently drift.
- **Hardware validation NOT claimed.** The signed/unsigned/mismatch display against a real signed zip is Phase-C/operator — see [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](../../../docs/MANUAL_VERIFICATION_CHECKLIST.md).

## Artifacts + SHA-256

MSI + NSIS installers + `SHA256SUMS.txt` produced by the CI release job, attached to the published
release (**unsigned**). Verify against that file:

- https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.9.3
