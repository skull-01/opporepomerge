---
description: Cut and publish the next version release (bump, evidence, PR, tag, styled GitHub release)
argument-hint: "[new version e.g. 2.9.14] — optional; defaults to next patch"
---

Runbook for cutting a full version-bump release of this Kodi add-on. Target version
from arguments (if given): $ARGUMENTS

## Target version
- If a version is given in the arguments, use it. Otherwise bump the patch of the
  current `resources/lib/version.py` `ADDON_VERSION` (e.g. 2.9.13 → 2.9.14).
- Always increment `BUILD_NUMBER` by 1. Use BUILD_ID/title text `v<new> Final`.
- Decide the release theme from the commits merged since the previous tag
  (`git log <prev-tag>..origin/main`). If there are no runtime changes, say so
  explicitly ("No runtime behavior changed").

## Steps
1. **Pre-flight**: `git fetch`; `gh pr list` (merge or note any open PRs first);
   create branch `release/v<new>` off `origin/main`.
2. **Bump active version** (`<prev>` → `<new>`):
   - `resources/lib/version.py`: ADDON_VERSION, BUILD_ID, BUILD_NUMBER (+1), RELEASE_LINE.
   - `pyproject.toml` `[project] version`.
   - `docs/sources.yaml`: version, build_number, build_id, title, source_recommendation.
   - Run `tools/sync_version.py --write` (sets addon.xml version attr), then manually
     update the addon.xml `<summary>` and PREPEND ONE new `<description>` sentence —
     keep the full historical narrative; never strip prior-version sentences.
   - `.github/workflows/ci.yml`: `EXPECTED_VERSION` + the two `*-<ver>-ci*.zip` names.
   - `scripts/verify.sh`: `EXPECTED_VERSION` default.
3. **Bump tests** (wholesale, `tests/` only): replace `<prev>` → `<new>`, and
   `BUILD_NUMBER == <N>` → `<N+1>` (also `build_number: <N>` and `build_number"] == <N>`).
   Update any test that pins the addon.xml summary text to the new summary.
   NEVER edit frozen evidence: `docs/release-history/`, `release-evidence/`,
   `docs/github-readiness/`, `docs/ai-handoff/` keep their historical versions. After a
   clean bump there are ~0 active refs to `<prev>` left (one historical line in addon.xml
   is expected).
4. **Regenerate docs**: `tools/render_docs.py --write` (README/reference/web-references).
   Do not hand-edit the generated blocks.
5. **New evidence set** in `docs/release-history/` (clone the previous set, rewrite for
   CURRENT reality — gate value, formatter, coverage %, what changed):
   `BUILD_NOTES_v<new>_FINAL.md`, `RELEASE_MANIFEST_v<new>.md`, `RELEASE_NOTES_v<new>.md`,
   `COVERAGE_REPORT_v<new>.md`, `TEST_AUDIT_REPORT_v<new>.md`, `HARDWARE_VALIDATION_v<new>.md`,
   `PRE_HARDWARE_AUDIT_REPORT_v<new>.md`, `HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v<new>.md`;
   plus `release-evidence/v<new>-final/MANIFEST.txt` listing all 8.
   Required content (checked by `tests/test_v2910_final_release.py`):
   - RELEASE_MANIFEST must list the 4 artifact names:
     `script.oppo203.iso.external-<new>.zip`, `-<new>-dev-source.zip`,
     `-<new>-artifacts-bundle.zip`, `-<new>.sha256`.
   - HARDWARE_VALIDATION, RELEASE_NOTES, HARDWARE_ECOSYSTEM_SUPPORT_MATRIX must each
     contain "software-verified", "not performed", and "not claimed".
6. **Verify** (fast loop): `tools/sync_version.py --check --expected-version <new>`,
   `tools/render_docs.py --check`, `tools/audit_release.py --expected-version <new>` (PASS),
   `ruff check resources default.py service.py` + `ruff format --check resources default.py service.py`,
   full suite `pytest -n auto`, and the SERIAL coverage gate `coverage run -m pytest`
   then `coverage report`. On Windows set `TEMP/TMP` to a repo-local dir,
   `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, and `--basetemp=build\_pt`; use the local `.venv`.
   Fix anything that fails before shipping.
7. **Ship**: commit `Release v<new> Final: <theme>`, push the branch, open a PR to
   `main`, and wait for CI. Report the check results — confirm the required gates
   (Release gate, Lint, Compatibility smoke, Build ZIP) are green before merging. Note
   that the `claude-review` check is currently failing due to a known broken bot/secret
   issue unrelated to the change; flag it so the maintainer can decide. Merge with a
   merge commit (`gh pr merge --merge`).
8. **Tag & publish**: annotated tag `v<new>` on the merge commit (`git tag -a v<new>
   origin/main -m "..."`), push it. `package.yml` builds the ZIP+SHA256 and creates the
   release. Watch that run, then set the title and styled body:
   `gh release edit v<new> --title "v<new> Final" --notes-file <file>` (use `--notes-file`
   to avoid shell-quoting issues — bodies often contain apostrophes).
9. **Update the handoff guide & memory.** Refresh `docs/ai-handoff/AI_RESUME_GUIDE.md` so
   it never goes stale — update the "Latest release" facts (§0, §1), the "Development
   journey" list (§8) with this release, and "Current state & next steps" (§9). Update the
   maintainer memory with the new latest version. Then report the published release URL.

## Release-notes style (GitHub release body)
Match this structure (modeled on the v2.9.10 release):

    Release Notes — v<new> Final

    <one-line intro>

    ## Highlights
    - <bullet>
    - <bullet>

    ## Runtime behavior
    <what changed, or "No runtime behavior changed in v<new>. ...preserved...">

    ## Hardware validation
    This package remains software-verified only. Hardware validation is not performed / not claimed.

## Reference
A correct prior bump is the best template: `git show <prev-release-commit>` shows the
exact file/line footprint (~78 files). This command is the canonical, self-contained
procedure.
