"""v2.9.1 Build 16 - diagnostic logging fallback refactor tests."""
from __future__ import annotations

import importlib
import io
import logging
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for item in (str(ROOT), str(LIB)):
    if item not in sys.path:
        sys.path.insert(0, item)


class FakeXbmc:
    LOGINFO = 1
    LOGWARNING = 2

    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def log(self, message: str, level: int) -> None:
        self.calls.append((message, level))


def test_fallback_uses_python_logging_stream_handler_not_direct_print(capsys):
    from resources.lib import diagnostic_logging

    formatted = diagnostic_logging.log_to_xbmc(None, "diag", "structured fallback")
    captured = capsys.readouterr().out

    assert formatted == "[OPPO203][DIAG] structured fallback"
    assert formatted in captured
    logger = logging.getLogger(diagnostic_logging.FALLBACK_LOGGER_NAME)
    assert any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers)


def test_kodi_logging_adapter_preserves_xbmc_log_behavior():
    from resources.lib import diagnostic_logging

    fake = FakeXbmc()
    formatted = diagnostic_logging.log_to_xbmc(fake, "wizard", "adapter path", level=fake.LOGWARNING)

    assert formatted == "[OPPO203][WIZARD] adapter path"
    assert fake.calls == [("[OPPO203][WIZARD] adapter path", fake.LOGWARNING)]


def test_external_player_log_remains_capture_compatible():
    sys.modules.pop("external_player", None)
    external_player = importlib.import_module("external_player")
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        external_player.log("Requested ISO: movie.iso")
    assert "[OPPO203][PLAYER] Requested ISO: movie.iso" in buffer.getvalue()


def test_oppo_remote_fallback_uses_shared_logging_helper(capsys):
    from resources.lib import oppo_remote

    oppo_remote.xbmc = None
    oppo_remote._log("fallback remote detail")
    captured = capsys.readouterr().out
    assert "[OPPO203][REMOTE] fallback remote detail" in captured


def test_addon_metadata_and_version_source_identify_build11():
    from resources.lib import version

    assert version.BUILD_ID == "v2.9.11 Final"
    assert version.BUILD_NUMBER == 20
    addon_text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.1 Build 11" in addon_text
    assert "diagnostic logging fallback refactor" in addon_text


def test_release_audit_requires_build11_manifest_and_evidence():
    spec = importlib.util.spec_from_file_location("audit_release_build11", ROOT / "tools" / "audit_release.py")
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)

    results = audit.run_audit(ROOT, expected_version="2.9.11")
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.1-build11/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.1_BUILD13.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.9.1_BUILD13.md" in names
    assert not [item for item in results if item["status"] != "ok"]
