# Release Manifest — v2.9.17 Final

Final artifacts:

- `script.oppo203.iso.external-2.9.17.zip`
- `script.oppo203.iso.external-2.9.17-dev-source.zip`
- `script.oppo203.iso.external-2.9.17-artifacts-bundle.zip`
- `script.oppo203.iso.external-2.9.17.sha256`

## Gate

The release uses the standard release gate: source checks (`py_compile`, `render_docs --check`, `sync_version --check`, `test_layout.py --check`, `i18n_extract.py --check`), targeted tests, the full pytest suite, unittest discovery, source coverage at the enforced 99% gate, release audit, runtime packaging, and runtime ZIP audit. Because v2.9.17 also touches the configurator's mirrored player database, the configurator gate (`tsc -b`, `vitest`, `vite build`) is run alongside.

## Runtime ZIP policy

The installable runtime ZIP excludes tests, tools, scripts, docs, release evidence, reports, handoff files, Markdown evidence files, caches, compiled Python files, and other development artifacts. The runtime add-on icon (`icon.png`) ships via the optional-asset allowlist. The new `resources/lib/oppo/dolby_vision.py` ships as add-on code; the research summary and the players-DB JSON live under `docs/` and are excluded.

## Hardware validation

This is a software-verified release. Real hardware validation was not performed or claimed.
