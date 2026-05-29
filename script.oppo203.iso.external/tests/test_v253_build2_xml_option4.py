"""v2.5.3 Build 2 - Option 4 conservative playercorefactory XML rules."""
from __future__ import annotations

import contextlib
import importlib
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
STUBS = ROOT / "tests" / "_stubs"
for item in (str(ROOT), str(LIB)):
    if item not in sys.path:
        sys.path.insert(0, item)


@contextlib.contextmanager
def kodi_stubs(*extra):
    from tests._support.lib_buckets import with_canonical
    names = {
        "xbmc", "xbmcaddon", "xbmcgui", "xbmcvfs", "xbmcplugin", "xbmcdrm",
        "resources.lib.installer", "installer",
    }
    names.update(extra)
    names = with_canonical(names)
    old_path = list(sys.path)
    saved = {name: sys.modules.get(name) for name in names}
    try:
        sys.path.insert(0, str(STUBS))
        sys.path.insert(0, str(ROOT))
        sys.path.insert(0, str(LIB))
        for name in names:
            sys.modules.pop(name, None)
        yield
    finally:
        for name in names:
            sys.modules.pop(name, None)
        for name, module in saved.items():
            if module is not None:
                sys.modules[name] = module
        sys.path[:] = old_path


@contextlib.contextmanager
def _installer(include_disc_folder_rules="true"):
    with kodi_stubs():
        import xbmcaddon
        xbmcaddon.reset(
            settings={
                "include_disc_folder_rules": include_disc_folder_rules,
                "python_path": "/usr/bin/python3",
            },
            info={"path": str(ROOT), "id": "script.oppo203.iso.external"},
        )
        yield importlib.import_module("resources.lib.installer")


def test_option4_xml_rules_are_tag_aware_and_disc_style_only():
    with _installer("true") as installer:
        xml = installer.build_rule_xml()
    assert "4K|4k|UHD|uhd|2160p|2160P" in xml
    assert 'filetypes="iso"' in xml
    assert 'filetypes="bdmv"' in xml
    assert 'filetypes="mpls"' in xml
    assert xml.count('player="Oppo203ISO"') == 3
    assert xml.count('filename="') == 3


def test_option4_xml_does_not_emit_broad_or_legacy_disc_rules():
    with _installer("true") as installer:
        xml = installer.build_rule_xml()
    forbidden_fragments = [
        '<rule filetypes="iso" player="Oppo203ISO"',
        'filetypes="bdmv|mpls|m2ts"',
        'filetypes="ifo|vob"',
        'filetypes="dat|cue|bin"',
        'dvdimage="true"',
        'dvdfile="true"',
        'VIDEO_TS',
        'MPEGAV',
        'SVCD',
    ]
    for fragment in forbidden_fragments:
        assert fragment not in xml


def test_option4_xml_excludes_loose_raw_video_filetypes():
    with _installer("true") as installer:
        xml = installer.build_rule_xml().lower()
    loose_filetypes = (
        "mkv", "mp4", "m4v", "mov", "mpg", "mpeg", "avi", "wmv",
        "flv", "webm", "ts", "m2ts", "mts", "m2t", "vob", "ogm",
        "ogv", "divx", "xvid", "3gp", "3g2", "f4v", "rm", "rmvb",
        "asf",
    )
    filetype_attrs = [part.split('"', 1)[0] for part in xml.split('filetypes="')[1:]]
    emitted = set("|".join(filetype_attrs).split("|"))
    for filetype in loose_filetypes:
        assert filetype not in emitted


def test_generated_full_playercorefactory_xml_is_well_formed():
    with _installer("true") as installer:
        xml = installer.build_snippet_xml_body()
    ET.fromstring(xml)


def test_disc_folder_setting_still_controls_bdmv_mpls_rules():
    with _installer("false") as installer:
        xml = installer.build_rule_xml()
    assert 'filetypes="iso"' in xml
    assert 'filetypes="bdmv"' not in xml
    assert 'filetypes="mpls"' not in xml
    assert "BDMV" not in xml


def test_installer_preserves_naming_warning_text():
    with _installer("true") as installer:
        warning = installer.build_xml_naming_warning_text()
    assert "4K external-player XML mode requires naming discipline" in warning
    assert "4K, UHD, or 2160p" in warning
    assert "Loose video files" in warning
    assert "metadata" in warning
    assert "ISO internals" in warning
