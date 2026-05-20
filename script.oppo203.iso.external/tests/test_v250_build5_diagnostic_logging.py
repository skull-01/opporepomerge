"""v2.5.0 Build 5 - diagnostic logging standardization tests."""
from __future__ import annotations

import importlib
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for path in (str(ROOT), str(LIB)):
    if path not in sys.path:
        sys.path.insert(0, path)


class FakeXbmc:
    LOGINFO = 1

    def __init__(self):
        self.calls = []

    def log(self, message, level):
        self.calls.append((message, level))


class TestV250Build5DiagnosticLogging(unittest.TestCase):
    def setUp(self):
        for name in ("diagnostic_logging", "external_player", "wizard"):
            sys.modules.pop(name, None)

    def test_format_log_message_standardizes_support_prefixes(self):
        logging = importlib.import_module("diagnostic_logging")
        self.assertEqual(
            logging.format_log_message("player", "Starting Oppo"),
            "[OPPO203][PLAYER] Starting Oppo",
        )
        self.assertEqual(
            logging.format_log_message("wizard", "cancelled"),
            "[OPPO203][WIZARD] cancelled",
        )
        self.assertEqual(
            logging.format_log_message("unknown_area", "detail"),
            "[OPPO203][UNKNOWN_AREA] detail",
        )

    def test_format_log_message_is_idempotent_for_existing_prefix(self):
        logging = importlib.import_module("diagnostic_logging")
        already = "[OPPO203][PLAYER] Already formatted"
        self.assertEqual(logging.format_log_message("player", already), already)

    def test_log_to_xbmc_returns_and_writes_standardized_message(self):
        logging = importlib.import_module("diagnostic_logging")
        fake = FakeXbmc()
        formatted = logging.log_to_xbmc(fake, "diag", "summary ready")
        self.assertEqual(formatted, "[OPPO203][DIAG] summary ready")
        self.assertEqual(fake.calls, [("[OPPO203][DIAG] summary ready", fake.LOGINFO)])

    def test_external_player_log_uses_player_prefix_without_behavior_dependency(self):
        external_player = importlib.import_module("external_player")
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            external_player.log("Requested ISO: movie.iso")
        self.assertIn("[OPPO203][PLAYER] Requested ISO: movie.iso", buffer.getvalue())

    def test_wizard_log_uses_wizard_prefix_when_kodi_logger_available(self):
        wizard = importlib.import_module("wizard")
        fake = FakeXbmc()
        wizard.xbmc = fake
        wizard._wizard_log("recovery state updated")
        self.assertEqual(fake.calls, [("[OPPO203][WIZARD] recovery state updated", fake.LOGINFO)])

    def test_service_prefix_is_standardized(self):
        service = importlib.import_module("service")
        self.assertEqual(service.LOG_PREFIX, "[OPPO203][SERVICE]")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
