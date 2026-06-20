"""OppoSvm3PlaybackMonitor -- verbose-mode-3 playback confirmation for OPPO UDP-20X.

This extends the persistent-TCP idea in ``oppo_tcp_client.py`` to OPPO's
documented verbose mode 3 (``#SVM 3``): query the current verbose mode
(``#QVM``) and remember it, switch to mode 3, then read CR/LF-terminated
``@UPL`` playback-status and ``@UTC`` time-code push lines.

The point of SVM3 is that playback is only treated as *confirmed* when the OPPO
itself reports it -- ``@UPL PLAY`` sets ``confirmed_playback`` and an *advancing*
``@UTC`` time code sets ``confirmed_progress`` -- never because a play command was
sent. The previous verbose mode is restored on exit, even on error.

The monitor is dependency-free and fully injectable (socket factory + monotonic
clock) so it runs hermetically under tests with no real device and no real time.
``hold_mode`` / the legacy monitors are untouched; this is a separate path that
PR A3 selects when ``playback_monitor_mode`` is ``svm3``.
"""

from __future__ import annotations

import socket
import time
from collections import deque
from collections.abc import Callable
from typing import Any

# @UPL values. Active/keep-alive states keep the session alive; the stop set ends
# it. These mirror oppo_tcp_client's vocabulary; a disc menu is treated as an
# active (navigable) session rather than a stop, which is finer than the legacy
# coarse stop detector and matches the SVM3 build plan's parsing policy.
_UPL_PLAY = {"PLAY", "FFWD", "FREV", "SFWD", "SREV"}
# LOADING is a keep-alive transient (the disc is mounting) but is NOT confirmed playback --
# only a real PLAY (or trick-play) state sets confirmed_playback.
_UPL_LOADING = {"LOADING"}
_UPL_PAUSE = {"PAUSE", "PAUS"}
_UPL_MENU = {"MENU", "DISC", "DISC MENU"}
_UPL_STOP = {
    "STOP",
    "STOPPED",
    "HOME",
    "HOME MENU",
    "MCTR",
    "MEDIA CENTER",
    "NO DISC",
    "NODISC",
}

_VERBOSE_MODES = {"0", "1", "2", "3"}

# Default tuning shipped as code constants (PR A2); persistent settings can be
# added later if operators need to tune them. Times are in seconds.
DEFAULT_SUMMARY_INTERVAL = 60.0
DEFAULT_RING_BUFFER_SIZE = 100
DEFAULT_STARTUP_TIMEOUT = 30.0
DEFAULT_SESSION_TIMEOUT = 14400.0  # 240 minutes
DEFAULT_CONNECT_TIMEOUT = 10.0
DEFAULT_RECV_TIMEOUT = 5.0


def _noop_log(_message: str) -> None:
    pass


def _parse_verbose_mode(line: str | None) -> str | None:
    """Pull the trailing verbose-mode digit from a #QVM reply.

    Accepts the documented response shapes -- "@QVM OK 2", "QVM OK 2", "OK 2" --
    by scanning tokens from the right for the first 0-3 digit.
    """
    if not line:
        return None
    for token in reversed(line.replace("@", " ").split()):
        if token in _VERBOSE_MODES:
            return token
    return None


def _upl_state_label(value: str) -> str:
    """Normalize a raw @UPL value to a status-model state token."""
    if value in _UPL_PLAY:
        return "PLAY"
    if value in _UPL_LOADING:
        return "LOADING"
    if value in _UPL_PAUSE:
        return "PAUS"
    if value in _UPL_MENU:
        return "MENU"
    if value in _UPL_STOP:
        if value.startswith("HOME"):
            return "HOME"
        if value in {"MCTR", "MEDIA CENTER"}:
            return "MCTR"
        return "STOP"
    return "unknown"


class OppoSvm3PlaybackMonitor:
    """Confirm OPPO playback/progress over a persistent verbose-mode-3 session."""

    def __init__(
        self,
        host: str,
        port: int | str,
        *,
        logger: Callable[[str], None] | None = None,
        full_event_log: bool = False,
        summary_interval: float = DEFAULT_SUMMARY_INTERVAL,
        ring_buffer_size: int = DEFAULT_RING_BUFFER_SIZE,
        startup_timeout: float = DEFAULT_STARTUP_TIMEOUT,
        session_timeout: float = DEFAULT_SESSION_TIMEOUT,
        require_progress: bool = True,
        restore_previous_mode: bool = True,
        connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
        recv_timeout: float = DEFAULT_RECV_TIMEOUT,
        sock_factory: Callable[[], Any] | None = None,
        monotonic: Callable[[], float] | None = None,
    ) -> None:
        self._host = host
        self._port = int(port)
        self._log = logger or _noop_log
        self._full_event_log = bool(full_event_log)
        self._summary_interval = float(summary_interval)
        self._startup_timeout = float(startup_timeout)
        self._session_timeout = float(session_timeout)
        self._require_progress = bool(require_progress)
        self._restore_previous_mode = bool(restore_previous_mode)
        self._connect_timeout = float(connect_timeout)
        self._recv_timeout = float(recv_timeout)
        self._sock_factory = sock_factory
        self._monotonic = monotonic or time.monotonic

        self._sock: Any = None
        self._buf = b""
        self._closed = False
        self._events: deque[str] = deque(maxlen=max(1, int(ring_buffer_size)))

        self.previous_verbose_mode: str | None = None
        self.confirmed_playback = False
        self.confirmed_progress = False
        self.playback_state = "unknown"
        self.first_utc: str | None = None
        self.last_utc: str | None = None
        self.utc_tick_count = 0
        self.last_event_at: float | None = None
        self.stop_reason: str | None = None

    # -- connection ---------------------------------------------------------

    def connect(self) -> None:
        """Open the TCP control connection. Raises OSError on failure."""
        if self._sock_factory is not None:
            self._sock = self._sock_factory()
        else:
            self._sock = socket.create_connection(
                (self._host, self._port), timeout=self._connect_timeout
            )
        self._sock.settimeout(self._recv_timeout)

    def _send(self, command: str) -> None:
        if self._sock is None:
            raise OSError("not connected")
        self._sock.sendall((command + "\r").encode("ascii"))

    def _pop_buffered_line(self) -> str | None:
        for sep in (b"\r\n", b"\r", b"\n"):
            idx = self._buf.find(sep)
            if idx >= 0:
                raw = self._buf[:idx]
                self._buf = self._buf[idx + len(sep) :]
                return raw.decode("ascii", errors="replace").strip()
        return None

    def _read_line(self) -> str | None:
        """Return the next complete line, or None on recv timeout / close."""
        while True:
            line = self._pop_buffered_line()
            if line is not None:
                return line
            try:
                chunk = self._sock.recv(1024)
            except socket.timeout:
                return None
            except OSError:
                self._closed = True
                return None
            if not chunk:
                self._closed = True
                return None
            self._buf += chunk

    # -- verbose-mode control ----------------------------------------------

    def query_previous_verbose_mode(self) -> str | None:
        """Send #QVM and remember the current verbose mode for restore()."""
        self._send("#QVM")
        self.previous_verbose_mode = _parse_verbose_mode(self._read_line())
        return self.previous_verbose_mode

    def enable(self) -> bool:
        """Switch the OPPO to verbose mode 3 and consume its (best-effort) ack."""
        self._send("#SVM 3")
        ack = self._read_line()
        if ack:
            self._events.append(ack)
        return True

    def restore(self) -> bool:
        """Restore the previously-seen verbose mode. Never raises."""
        if not self._restore_previous_mode or self.previous_verbose_mode is None:
            return False
        try:
            self._send(f"#SVM {self.previous_verbose_mode}")
        except OSError:
            return False
        return True

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    # -- event handling -----------------------------------------------------

    def _handle_line(self, line: str) -> bool:
        """Update state from one push line. Returns True on a terminal stop."""
        self._events.append(line)
        if self._full_event_log:
            self._log(f"SVM3 raw: {line}")

        norm = line.strip()
        if norm.startswith("@"):
            norm = norm[1:]
        parts = norm.split(None, 1)
        if not parts:
            return False
        code = parts[0].upper()
        rest = parts[1].strip() if len(parts) > 1 else ""
        if code == "UPL":
            self.last_event_at = self._monotonic()
            return self._handle_upl(rest)
        if code == "UTC":
            self.last_event_at = self._monotonic()
            self._handle_utc(rest)
        return False

    def _handle_upl(self, value: str) -> bool:
        v = value.upper().strip()
        prev_state = self.playback_state
        self.playback_state = _upl_state_label(v)
        if self.playback_state == "PLAY":
            self.confirmed_playback = True
        terminal = v in _UPL_STOP
        if terminal:
            self.stop_reason = self.stop_reason or f"oppo_{self.playback_state.lower()}"
        if self.playback_state != prev_state:
            self._log(f"SVM3 state: {prev_state} -> {self.playback_state}")
        return terminal

    def _handle_utc(self, rest: str) -> None:
        code = rest.strip()
        if not code:
            return
        if self.first_utc is None:
            self.first_utc = code
            self.last_utc = code
            self.utc_tick_count = 1
            return
        if code != self.last_utc:
            self.utc_tick_count += 1
            self.confirmed_progress = True
            self.last_utc = code

    # -- main loop ----------------------------------------------------------

    def listen_until_done(self, stop_event: Any = None) -> dict[str, Any]:
        """Read push events until a stop/timeout/stop_event. Returns snapshot()."""
        start = self._monotonic()
        last_summary = start
        while True:
            if stop_event is not None and stop_event.is_set():
                self.stop_reason = self.stop_reason or "stop_event"
                break
            elapsed = self._monotonic() - start
            if elapsed >= self._session_timeout:
                self.stop_reason = self.stop_reason or "session_timeout"
                break
            # last_event_at is set only by @UPL/@UTC playback-status pushes (not by @UVO/@UAU
            # resolution chatter), so a never-playing-but-chatty device still hits this timeout.
            if self.last_event_at is None and elapsed >= self._startup_timeout:
                self.stop_reason = self.stop_reason or "startup_timeout"
                break

            line = self._read_line()
            if line is None and self._closed:
                self.stop_reason = self.stop_reason or "connection_closed"
                break

            terminal = self._handle_line(line) if line is not None else False

            now = self._monotonic()
            if now - last_summary >= self._summary_interval:
                self._log_summary()
                last_summary = now
            if terminal:
                break
        return self.snapshot()

    # -- reporting ----------------------------------------------------------

    def is_confirmed(self) -> bool:
        if not self.confirmed_playback:
            return False
        if self._require_progress and not self.confirmed_progress:
            return False
        return True

    def _log_summary(self) -> None:
        self._log(
            f"SVM3 summary: state={self.playback_state} confirmed_playback={self.confirmed_playback} confirmed_progress={self.confirmed_progress} "
            f"utc_ticks={self.utc_tick_count} events={len(self._events)}"
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "monitor_mode": "svm3",
            "previous_verbose_mode": self.previous_verbose_mode,
            "oppo_playback_state": self.playback_state,
            "confirmed_playback": self.confirmed_playback,
            "confirmed_progress": self.confirmed_progress,
            "confirmed": self.is_confirmed(),
            "first_utc": self.first_utc,
            "last_utc": self.last_utc,
            "utc_tick_count": self.utc_tick_count,
            "stop_reason": self.stop_reason,
            "event_count": len(self._events),
            "last_raw_events": list(self._events),
        }
