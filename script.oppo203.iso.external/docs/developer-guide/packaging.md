# Developer Guide — Packaging

## Package types

The project uses three package concepts:

| Package | Purpose |
|---|---|
| Runtime ZIP | Installable Kodi add-on package. Must be clean and runtime-only. |
| Dev-source ZIP | Full source package for reconstruction, tests, tools, docs, and evidence. |
| Artifact bundle | Build reports, manifests, handoffs, checksums, and release evidence. |

## Runtime ZIP policy

The runtime ZIP must be installable by Kodi and must not contain development-only files.

Do not include:

- `tests/`
- `tools/`
- `scripts/`
- `docs/`
- `release-evidence/`
- `.github/`
- build notes
- AI handoff files
- coverage reports
- audit reports

## Package command

Preferred packaging command:

```bash
BUILD_SUFFIX=github-g3 OUT_DIR=/path/to/dist bash scripts/package_release.sh
```

The script creates:

```text
script.oppo203.iso.external-2.9.10-github-g3.zip
script.oppo203.iso.external-2.9.10-github-g3.sha256
script.oppo203.iso.external-2.9.10-github-g3-dev-source.zip
```

## Dev-source package

The dev-source package may contain:

- source files
- tests
- tools
- scripts
- docs
- release evidence
- GitHub metadata
- handoff documents

It should exclude cache/build byproducts such as:

- `__pycache__/`
- `.pytest_cache/`
- `.coverage`
- `.git/`

## Artifact bundle

Each build should include an artifact bundle containing at least:

- build notes
- release/change manifest
- test audit report
- coverage report when applicable
- hardware validation status
- AI handoff
- combined historical reconstruction handoff
- checksums

## Checksum rule

Create SHA256 checksums for public packages. A checksum file should identify each generated package clearly.

## Clean unpack rule

Before finalizing a build, unpack the dev-source ZIP into a clean directory and run the practical validation commands. This proves that the package can reconstruct the build state.
