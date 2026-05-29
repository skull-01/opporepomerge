#!/usr/bin/env python3
"""Synchronize/check addon.xml against resources.lib.version.

This helper keeps version identity explicit without making addon.xml import
Python at Kodi runtime. Use ``--check`` in CI/audit flows and ``--write`` when
intentionally updating addon.xml from the Python version source.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def project_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "addon.xml").exists() and (candidate / "resources" / "lib" / "kodi" / "version.py").exists():
            return candidate
    raise RuntimeError("Could not find add-on root containing addon.xml and resources/lib/kodi/version.py")


def _import_version(root: Path):
    for path in (str(root), str(root / "resources" / "lib")):
        if path not in sys.path:
            sys.path.insert(0, path)
    try:
        from resources.lib.kodi import version as version_module  # type: ignore
    except Exception:
        import version as version_module  # type: ignore
    return version_module


def version_source(root: Path) -> str:
    return str(_import_version(root).ADDON_VERSION)


def addon_xml_version(root: Path) -> str:
    return ET.parse(root / "addon.xml").getroot().attrib.get("version", "")


def check_version_consistency(root: Path, expected_version: str | None = None) -> tuple[bool, str]:
    source = version_source(root)
    xml_version = addon_xml_version(root)
    if expected_version is not None and source != expected_version:
        return False, f"version.py ADDON_VERSION={source}; expected {expected_version}"
    if xml_version != source:
        return False, f"addon.xml version={xml_version}; version.py ADDON_VERSION={source}"
    return True, f"addon.xml and version.py agree on {source}"


def write_addon_xml_version(root: Path) -> str:
    source = version_source(root)
    addon_path = root / "addon.xml"
    text = addon_path.read_text(encoding="utf-8")
    new_text, count = __import__('re').subn(r'(<addon\b[^>]*\bversion=")([^"]+)(")', rf'\g<1>{source}\g<3>', text, count=1)
    if count != 1:
        raise RuntimeError("Could not find addon version attribute to update")
    addon_path.write_text(new_text, encoding="utf-8")
    return source


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check or sync addon.xml version against resources.lib.version")
    parser.add_argument("--root", default=".")
    parser.add_argument("--expected-version", default=None)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="check only; default behavior")
    group.add_argument("--write", action="store_true", help="write addon.xml version from version.py")
    args = parser.parse_args(argv)
    root = project_root(Path(args.root))
    if args.write:
        written = write_addon_xml_version(root)
        print(f"Updated addon.xml version to {written}")
    ok, detail = check_version_consistency(root, expected_version=args.expected_version)
    print(("OK" if ok else "FAIL") + f": version_consistency - {detail}")
    return 0 if ok else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
