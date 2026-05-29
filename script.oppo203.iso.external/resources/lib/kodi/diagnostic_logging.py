"""Diagnostic logging helpers for OPPO ISO External.

Build 11 keeps Kodi ``xbmc.log`` as the preferred runtime sink and replaces
the old direct-print fallback with a small Python logging fallback. The public
``log_to_xbmc`` helper still returns the formatted message for tests and
callers, and stdout capture remains supported through a StreamHandler fallback.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

ADDON_LOG_TAG = "OPPO203"
FALLBACK_LOGGER_NAME = "oppo203.diagnostic"

LOG_CATEGORY_PREFIXES = {
    "setup": "SETUP",
    "wizard": "WIZARD",
    "player": "PLAYER",
    "service": "SERVICE",
    "remote": "REMOTE",
    "iso": "ISO",
    "tv": "TV",
    "diag": "DIAG",
    "config": "CONFIG",
}


def normalize_category(category: str | None) -> str:
    """Return a stable uppercase log category for support triage."""
    key = str(category or "diag").strip().lower()
    return LOG_CATEGORY_PREFIXES.get(key, key.upper() if key else "DIAG")


def format_log_message(category: str | None, message: object) -> str:
    """Format a support-friendly log message.

    Examples
    --------
    >>> format_log_message("player", "Starting Oppo")
    '[OPPO203][PLAYER] Starting Oppo'
    """
    text = str(message)
    prefix = f"[{ADDON_LOG_TAG}][{normalize_category(category)}]"
    if text.startswith(prefix):
        return text
    return f"{prefix} {text}"


class KodiLogHandler(logging.Handler):
    """Python logging handler that forwards records to Kodi's ``xbmc.log``."""

    def __init__(self, xbmc_module: Any, kodi_level: int | None = None) -> None:
        super().__init__()
        self.xbmc_module = xbmc_module
        self.kodi_level = kodi_level

    def emit(self, record: logging.LogRecord) -> None:
        level = self.kodi_level
        if level is None:
            level = getattr(self.xbmc_module, "LOGINFO", 1)
        self.xbmc_module.log(self.format(record), level)


def fallback_logger() -> logging.Logger:
    """Return the structured Python fallback logger.

    The handler stream is refreshed on each call so tests that redirect or
    capture ``sys.stdout`` continue to observe fallback diagnostics without
    relying on direct ``print()`` calls.
    """
    logger = logging.getLogger(FALLBACK_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    else:
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.stream = sys.stdout
    return logger


def _log_with_python_fallback(formatted: str) -> None:
    fallback_logger().info(formatted)


def log_to_xbmc(xbmc_module, category: str | None, message: object, level=None) -> str:
    """Write a formatted message to Kodi or the structured fallback logger.

    The formatted string is returned so tests and diagnostic callers can assert
    the exact support prefix without depending on Kodi.
    """
    formatted = format_log_message(category, message)
    if xbmc_module and hasattr(xbmc_module, "log"):
        log_level = level if level is not None else getattr(xbmc_module, "LOGINFO", 1)
        logger = logging.getLogger(f"{FALLBACK_LOGGER_NAME}.kodi")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        handler = KodiLogHandler(xbmc_module, log_level)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.handlers = [handler]
        logger.info(formatted)
    else:
        _log_with_python_fallback(formatted)
    return formatted
