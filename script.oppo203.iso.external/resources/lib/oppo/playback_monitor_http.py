"""OppoHttpPlaybackMonitor -- pure-HTTP/436 playback confirmation for the http monitor axis.

The 7th preset (``http_handoff_http``) launches over HTTP and confirms playback by polling the
OPPO HTTP API (``/getglobalinfo`` + ``/getplayingtime``) every ``oppo_http_refresh_seconds``,
instead of the SVM3 TCP push stream or the legacy hold. Playback is only treated as *confirmed*
when the player's own ``/getglobalinfo`` reports it; an advancing ``/getplayingtime`` sets
``confirmed_progress`` -- never because a launch command was sent.

Fallback-safe: if the very first poll cannot reach the player, ``run()`` returns ``None`` so the
caller (``playback_session._dispatch_monitor``) drops to the legacy hold -- exactly like the SVM3
monitor's connect-failure path. Fully injectable (fetchers + clock + sleep) so it runs
hermetically under tests with no real device and no real time.

This is a separate path selected when ``playback_monitor_mode`` is ``http``; the legacy/svm3
monitors are untouched. The HTTP API is community-reverse-engineered (Xnoppo V3 adoption) -- not
an official OPPO protocol claim, and not hardware-validated.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

DEFAULT_STARTUP_TIMEOUT = 30.0
DEFAULT_SESSION_TIMEOUT = 14400.0  # 240 minutes, matching the SVM3 monitor
DEFAULT_IDLE_CONFIRMATIONS = 2
DEFAULT_MAX_POLL_FAILURES = 3

# getplayingtime fields that carry an elapsed/position token; the first present one is tracked.
_TIME_KEYS = ("playtime", "elapsed", "position", "cur_time", "current", "time")

# OppoError is a RuntimeError; a raw socket failure is an OSError. Catching this pair covers
# "the player is unreachable / the HTTP call failed" without a blind except.
_TRANSPORT_ERRORS = (RuntimeError, OSError)


def _noop_log(_message: str) -> None:
    pass


def _play_time_token(info: Any) -> str:
    """Return the first present elapsed/position token from a getplayingtime payload."""
    if not isinstance(info, dict):
        return ""
    for key in _TIME_KEYS:
        val = info.get(key)
        if val not in (None, ""):
            return str(val).strip()
    return ""


class OppoHttpPlaybackMonitor:
    """Confirm OPPO playback/progress by polling the HTTP API until idle or timeout."""

    def __init__(
        self,
        settings: Any,
        *,
        logger: Callable[[str], None] | None = None,
        fetch_info: Callable[[Any], Any] | None = None,
        fetch_time: Callable[[Any], Any] | None = None,
        is_playing: Callable[[Any], bool] | None = None,
        sleep: Callable[[float], None] | None = None,
        monotonic: Callable[[], float] | None = None,
        require_progress: bool = True,
        startup_timeout: float = DEFAULT_STARTUP_TIMEOUT,
        session_timeout: float = DEFAULT_SESSION_TIMEOUT,
        idle_confirmations: int = DEFAULT_IDLE_CONFIRMATIONS,
        max_poll_failures: int = DEFAULT_MAX_POLL_FAILURES,
    ) -> None:
        self._settings = settings
        self._log = logger or _noop_log
        self._fetch_info = fetch_info
        self._fetch_time = fetch_time
        self._is_playing = is_playing
        self._sleep = sleep or time.sleep
        self._monotonic = monotonic or time.monotonic
        self._require_progress = bool(require_progress)
        self._startup_timeout = float(startup_timeout)
        self._session_timeout = float(session_timeout)
        self._idle_confirmations = max(1, int(idle_confirmations))
        self._max_failures = max(1, int(max_poll_failures))
        self._refresh = max(1.0, float(settings.get("oppo_http_refresh_seconds", "5") or "5"))

        self.confirmed_playback = False
        self.confirmed_progress = False
        self.playback_state = "unknown"
        self.poll_count = 0
        self.progress_ticks = 0
        self.first_play_time: str | None = None
        self.last_play_time: str | None = None
        self.stop_reason: str | None = None

    def _resolve(self) -> tuple[Callable[[Any], Any], Callable[[Any], Any], Callable[[Any], bool]]:
        """Resolve the (info, time, is_playing) fetchers, defaulting to oppo_control."""
        if self._fetch_info and self._fetch_time and self._is_playing:
            return self._fetch_info, self._fetch_time, self._is_playing
        try:
            from . import oppo_control as oc
        except ImportError:  # pragma: no cover - bare-name fallback (run as __main__)
            import oppo_control as oc  # type: ignore[no-redef]
        return (
            self._fetch_info or oc.get_global_info,
            self._fetch_time or oc.get_playing_time,
            self._is_playing or oc.global_info_is_playing,
        )

    def run(self) -> dict[str, Any] | None:
        """Poll until playback ends or times out. Return the snapshot, or None if unreachable."""
        fetch_info, fetch_time, is_playing = self._resolve()

        try:
            info = fetch_info(self._settings)
        except _TRANSPORT_ERRORS as exc:
            self._log(f"HTTP monitor could not reach the player ({exc}); falling back to hold.")
            return None

        start = self._monotonic()
        idle_streak = 0
        failures = 0
        self._observe(info, is_playing, fetch_time)
        while True:
            elapsed = self._monotonic() - start
            if elapsed >= self._session_timeout:
                self.stop_reason = self.stop_reason or "session_timeout"
                break
            if not self.confirmed_playback and elapsed >= self._startup_timeout:
                self.stop_reason = self.stop_reason or "startup_timeout"
                break

            self._sleep(self._refresh)
            try:
                info = fetch_info(self._settings)
            except _TRANSPORT_ERRORS:
                failures += 1
                if failures >= self._max_failures:
                    self.stop_reason = self.stop_reason or "connection_lost"
                    break
                continue
            failures = 0

            playing = self._observe(info, is_playing, fetch_time)
            if self.confirmed_playback and not playing:
                idle_streak += 1
                if idle_streak >= self._idle_confirmations:
                    self.stop_reason = self.stop_reason or "oppo_idle"
                    break
            else:
                idle_streak = 0
        self._log(
            f"HTTP monitor ended: stop_reason={self.stop_reason} confirmed={self.is_confirmed()}"
        )
        return self.snapshot()

    def _observe(
        self, info: Any, is_playing: Callable[[Any], bool], fetch_time: Callable[[Any], Any]
    ) -> bool:
        self.poll_count += 1
        playing = bool(is_playing(info))
        prev = self.playback_state
        self.playback_state = "PLAY" if playing else "STOP"
        if playing:
            self.confirmed_playback = True
            self._track_progress(fetch_time)
        if self.playback_state != prev:
            self._log(f"HTTP monitor state: {prev} -> {self.playback_state}")
        return playing

    def _track_progress(self, fetch_time: Callable[[Any], Any]) -> None:
        try:
            token = _play_time_token(fetch_time(self._settings))
        except _TRANSPORT_ERRORS:
            return
        if not token:
            return
        if self.first_play_time is None:
            self.first_play_time = token
            self.last_play_time = token
            return
        if token != self.last_play_time:
            self.last_play_time = token
            self.progress_ticks += 1
            self.confirmed_progress = True

    def is_confirmed(self) -> bool:
        if not self.confirmed_playback:
            return False
        if self._require_progress and not self.confirmed_progress:
            return False
        return True

    def snapshot(self) -> dict[str, Any]:
        return {
            "monitor_mode": "http",
            "confirmed_playback": self.confirmed_playback,
            "confirmed_progress": self.confirmed_progress,
            "confirmed": self.is_confirmed(),
            "oppo_playback_state": self.playback_state,
            "stop_reason": self.stop_reason,
            "poll_count": self.poll_count,
            "progress_tick_count": self.progress_ticks,
            "first_play_time": self.first_play_time,
            "last_play_time": self.last_play_time,
        }
