"""Guard: the README front-page "Current release" section must track the active version.

The hand-written **Current status** blurb and **Current release** table live OUTSIDE the
`render_docs` generated block, so `render_docs --write` does not update them -- and they went
stale across releases (they lagged at add-on v2.9.16 / configurator v0.8.5 while the repo's
Latest was already configurator v0.9.6). This pins the add-on fields to
`resources/lib/kodi/version.py` so a release that forgets to refresh the front page fails CI.
The Windows-configurator line is norm-enforced (the add-on repo cannot know the configurator's
latest tag at test time) -- see AGENTS.md "The README front-page status is part of every release".
"""

from pathlib import Path

from resources.lib.kodi import version

ROOT = Path(__file__).resolve().parents[1]


def test_readme_current_release_tracks_active_version():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"| Add-on version | `{version.ADDON_VERSION}` |" in readme
    assert f"| Build identity | `{version.BUILD_ID}` |" in readme
    assert f"script.oppo203.iso.external-{version.ADDON_VERSION}.zip" in readme
    # The Current status blurb names the active build identity too.
    assert f"add-on **{version.BUILD_ID}**" in readme
