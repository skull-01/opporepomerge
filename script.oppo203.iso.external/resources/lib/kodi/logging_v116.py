"""Leveled logger, rotating file, and sensitive-data scrubber (v1.1.6).

A self-contained, dependency-free logger that:
  - filters by DEBUG/INFO/WARN/ERROR level
  - rotates a file in addon_data when it exceeds a byte budget
  - keeps a configurable number of historical rotations
  - scrubs MACs and IPv4 addresses out of every line before write

All filesystem and clock work flows through injection points so the
unit suite is fully hermetic.

Public API
----------
- LEVELS: tuple of level names in increasing severity
- level_value(name) -> int
- scrub(text)       -> str         (mask MACs and IPv4 addresses)
- Logger(path, *, level="INFO", max_bytes=131072, backups=3,
         fs=None, clock=None)
    .log(level, msg, *args)        - format-then-scrub-then-write
    .debug/info/warn/error(msg, *args)
    .set_level(name)
    .rotate()                      - manual force-rotate
"""

from __future__ import annotations

import os
import re as _re
import time as _time
from collections.abc import Callable
from typing import Protocol, overload

LEVELS = ("DEBUG", "INFO", "WARN", "ERROR")
_LEVEL_INDEX = {n: i for i, n in enumerate(LEVELS)}


def level_value(name: object) -> int:
    """Numeric value for a level name; returns -1 for unknown names."""
    if not name:
        return -1
    return _LEVEL_INDEX.get(str(name).upper(), -1)


# ---------------------------------------------------------------------
# Scrubber
# ---------------------------------------------------------------------

_MAC_RE = _re.compile(r"\b([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b")
_IPV4_RE = _re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


@overload
def scrub(text: str) -> str: ...  # pragma: no cover


@overload
def scrub(text: None) -> None: ...  # pragma: no cover


def scrub(text: object) -> object:
    """Mask MAC and IPv4 addresses for shareable logs.

    - MAC -> xx:xx:xx:xx:xx:xx (handles both colon and dash separators)
    - IPv4 -> x.x.x.x
    - 127.0.0.1 is preserved (loopback is never sensitive)
    - None / empty input is returned unchanged
    """
    if text is None or text == "":
        return text
    s = str(text)
    s = _MAC_RE.sub("xx:xx:xx:xx:xx:xx", s)
    # Preserve loopback specifically
    s = s.replace("127.0.0.1", "__LOOPBACK_MARKER__")
    s = _IPV4_RE.sub("x.x.x.x", s)
    s = s.replace("__LOOPBACK_MARKER__", "127.0.0.1")
    return s


# ---------------------------------------------------------------------
# Filesystem injection
# ---------------------------------------------------------------------


class _FsLike(Protocol):
    def exists(self, p: str) -> bool: ...  # pragma: no cover

    def size(self, p: str) -> int: ...  # pragma: no cover

    def append(self, p: str, text: str) -> None: ...  # pragma: no cover

    def rename(self, src: str, dst: str) -> None: ...  # pragma: no cover

    def remove(self, p: str) -> None: ...  # pragma: no cover


class _RealFS:
    def exists(self, p: str) -> bool:
        return os.path.exists(p)

    def size(self, p: str) -> int:
        try:
            return os.path.getsize(p)
        except OSError:
            return 0

    def read(self, p: str) -> str:
        with open(p, "r", encoding="utf-8") as f:
            return f.read()

    def append(self, p: str, text: str) -> None:
        d = os.path.dirname(p)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(text)

    def rename(self, src: str, dst: str) -> None:
        if os.path.exists(dst):
            try:
                os.remove(dst)
            except OSError:
                pass
        os.replace(src, dst)

    def remove(self, p: str) -> None:
        try:
            os.remove(p)
        except OSError:
            pass


# ---------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------


class Logger:
    """Leveled, size-rotating, scrubbing logger."""

    def __init__(
        self,
        path: str,
        *,
        level: str = "INFO",
        max_bytes: int = 131072,
        backups: int = 3,
        fs: _FsLike | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self.path = path
        self.level_name = level.upper() if level else "INFO"
        self._level = level_value(self.level_name)
        if self._level < 0:
            raise ValueError("unknown level: " + str(level))
        self.max_bytes = int(max_bytes)
        self.backups = max(0, int(backups))
        self.fs = fs if fs is not None else _RealFS()
        self.clock = clock if clock is not None else _time.time

    # -- level control --

    def set_level(self, name: str) -> None:
        v = level_value(name)
        if v < 0:
            raise ValueError("unknown level: " + str(name))
        self._level = v
        self.level_name = name.upper()

    def is_enabled(self, name: object) -> bool:
        v = level_value(name)
        return v >= 0 and v >= self._level

    # -- formatting --

    def _ts(self) -> str:
        t = _time.localtime(self.clock())
        return _time.strftime("%Y-%m-%d %H:%M:%S", t)

    def _format(self, level_name: str, msg: str, args: tuple[object, ...]) -> str:
        if args:
            try:
                msg = msg % args
            except Exception:
                msg = msg + " " + repr(args)
        line = "[" + self._ts() + "] " + level_name + " " + str(msg)
        return scrub(line) + "\n"

    # -- rotation --

    def _rotate_if_needed(self, incoming_bytes: int) -> None:
        if self.max_bytes <= 0:
            return
        cur = self.fs.size(self.path) if self.fs.exists(self.path) else 0
        if cur + incoming_bytes <= self.max_bytes:
            return
        self.rotate()

    def rotate(self) -> None:
        """Cascade .N -> .N+1, drop oldest beyond `backups`."""
        if not self.fs.exists(self.path):
            return
        # Drop the file that would exceed `backups`.
        oldest = self.path + "." + str(self.backups)
        if self.fs.exists(oldest):
            self.fs.remove(oldest)
        # Cascade .N -> .N+1 from highest down to .1
        for i in range(self.backups, 0, -1):
            src = self.path + "." + str(i - 1) if i > 1 else self.path
            dst = self.path + "." + str(i)
            if self.fs.exists(src):
                self.fs.rename(src, dst)
        # If backups=0, simply remove current.
        if self.backups == 0 and self.fs.exists(self.path):
            self.fs.remove(self.path)

    # -- main --

    def log(self, level_name: str, msg: str, *args: object) -> None:
        if not self.is_enabled(level_name):
            return
        line = self._format(level_name.upper(), msg, args)
        self._rotate_if_needed(len(line.encode("utf-8")))
        self.fs.append(self.path, line)

    def debug(self, msg: str, *a: object) -> None:
        self.log("DEBUG", msg, *a)

    def info(self, msg: str, *a: object) -> None:
        self.log("INFO", msg, *a)

    def warn(self, msg: str, *a: object) -> None:
        self.log("WARN", msg, *a)

    def error(self, msg: str, *a: object) -> None:
        self.log("ERROR", msg, *a)
