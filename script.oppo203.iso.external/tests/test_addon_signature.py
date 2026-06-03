"""Add-on build-tag (integrity manifest) tests + the cross-language contract.

``package_installable_zip.compute_manifest_sig`` stamps ``resources/oppokodiaddon.sig`` into the
installable zip; the configurator's Rust ``addon_manifest_sig`` recomputes + verifies it. The
manifest format is the cross-language contract: this test and the Rust test both pin the SAME
``FIXTURE_SIG`` for the SAME fixture, so the two implementations cannot silently drift.
"""

import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.join(ROOT, "tools") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "tools"))

import package_installable_zip as pkg  # noqa: E402

SIG_ARCNAME = "script.oppo203.iso.external/resources/oppokodiaddon.sig"

# Shared cross-language fixture. configurator/src-tauri/src/lib.rs `addon_manifest_sig` pins the
# identical members + FIXTURE_SIG. If either side changes the manifest format, one test fails.
FIXTURE = [
    (
        "script.oppo203.iso.external/addon.xml",
        b'<addon id="script.oppo203.iso.external" version="9.9.9"/>',
    ),
    ("script.oppo203.iso.external/default.py", b"print('x')\n"),
    ("script.oppo203.iso.external/resources/lib/__init__.py", b""),
]
FIXTURE_SIG = "bbcc638215a0e5be93c6c7a548cfc8cea1a806fd45cd47aeaf8b457043ee11fa"


def test_manifest_sig_matches_fixture_and_is_order_independent():
    assert pkg.compute_manifest_sig(FIXTURE) == FIXTURE_SIG
    assert pkg.compute_manifest_sig(list(reversed(FIXTURE))) == FIXTURE_SIG


def test_created_zip_carries_a_verifying_build_tag(tmp_path):
    out = tmp_path / "addon.zip"
    names = pkg.create_installable_zip(Path(ROOT), out)
    assert SIG_ARCNAME in names
    with zipfile.ZipFile(out) as zf:
        assert set(zf.namelist()) == set(names)  # the allowlist invariant still holds
        payload = json.loads(zf.read(SIG_ARCNAME))
        assert payload["addon"] == "script.oppo203.iso.external"
        assert payload["alg"] == "oppocfg-manifest-sha256-v1"
        assert len(payload["sig"]) == 64
        members = [(n, zf.read(n)) for n in zf.namelist() if n != SIG_ARCNAME]
        assert payload["sig"] == pkg.compute_manifest_sig(members)
        assert payload["files"] == len(members)
