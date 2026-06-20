"""v2.9.1 Build 8 settings exception narrowing regression tests."""

from __future__ import annotations

import inspect
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from resources.lib import settings_reader as sr


class BadStr:
    def __str__(self):
        raise RuntimeError("broken __str__")


class BadMapping:
    data = object()


def _source_of(name: str) -> str:
    return inspect.getsource(getattr(sr, name))


def test_low_risk_settings_parsers_no_longer_catch_broad_exception():
    for name in ("read_settings", "save_settings", "_firmware_major_build"):
        source = _source_of(name)
        assert "except Exception" not in source
    cls_source = inspect.getsource(sr.Settings)
    for method_name in ("get_int", "get_float"):
        start = cls_source.index(f"    def {method_name}")
        following = cls_source.find("\n    def ", start + 1)
        method_source = cls_source[start : following if following != -1 else len(cls_source)]
        assert "except Exception" not in method_source


def test_narrowed_numeric_parsers_preserve_legacy_fallbacks():
    settings = sr.Settings({"bad_int": "not-int", "bad_float": "not-float", "bad_text": BadStr()})
    assert settings.get_int("bad_int", 7) == 7
    assert settings.get_int("bad_text", 8) == 8
    assert settings.get_float("bad_float", 2.5) == 2.5
    assert settings.get_float("bad_text", 3.5) == 3.5
    assert settings.get_bool("bad_text", False) is False


def test_read_settings_catches_parse_and_os_errors_without_broad_exception(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        settings_xml = Path(td) / "settings.xml"
        settings_xml.write_text("<settings><setting", encoding="utf-8")
        parsed = sr.read_settings(td)
        assert parsed.get("_settings_read_error")

        def raise_os_error(_path):
            raise OSError("disk unavailable")

        monkeypatch.setattr(sr.ET, "parse", raise_os_error)
        parsed = sr.read_settings(td)
        assert "disk unavailable" in parsed.get("_settings_read_error")


def test_save_settings_narrowed_mapping_and_parse_fallbacks(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "settings.xml"
        path.write_text("<settings><setting", encoding="utf-8")
        assert sr.save_settings(td, BadMapping()) is True
        ET.parse(path)  # written file is valid after corrupt input fallback

        def raise_parse_error(_path):
            raise ET.ParseError("bad xml")

        monkeypatch.setattr(sr.ET, "parse", raise_parse_error)
        assert sr.save_settings(td, sr.Settings({"oppo_ip": "192.0.2.8"})) is True
        assert "192.0.2.8" in path.read_text(encoding="utf-8")


def test_firmware_major_build_uses_narrow_value_errors():
    assert sr._firmware_major_build("20X-65-0131") == 65
    assert sr._firmware_major_build("not-a-firmware") is None
    assert sr._firmware_major_build(None) is None
