"""Shared playback-session engine for the six-option playback architecture.

Both entry points run the *same* sequence:

* ``external_player.main()`` -- playercorefactory routing, and
* ``service._run_interception()`` -- service-interception routing

mark the session active -> ``fast_start`` (TV switch + AVR pre-sequence + OPPO
start) -> hold/monitor until playback ends -> ``fast_return`` (stop + AVR/TV
restore) -> clear the session. This module is that single sequence, so the
routings can never drift apart. When the resolved routing is ``http_handoff`` the
launch step uses ``fast_start_http`` (the community OPPO HTTP file launch) instead
of the TCP/disc start; the monitor axis (legacy/svm3) is unchanged.

The monitor branch is chosen by ``playback_monitor_mode`` (resolved through
``settings_reader.normalize_architecture``): ``legacy`` runs the existing
``external_player.hold_playback`` dispatcher unchanged; ``svm3`` runs the
``OppoSvm3PlaybackMonitor`` and, if it cannot connect, falls back to the legacy
hold. A split-truth status JSON (``oppo203iso-status.json``) is written next to
the session sentinel so playback confirmation is reported honestly rather than
as a single success flag.
"""

from __future__ import annotations

import json
import os
import traceback
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .settings_reader import Settings

try:
    from .settings_reader import normalize_architecture
except ImportError:  # pragma: no cover - bare-name fallback (run as __main__)
    from settings_reader import normalize_architecture  # type: ignore[no-redef]


STATUS_FILENAME = "oppo203iso-status.json"


def _external_player() -> Any:
    """Return the external_player module (lazy, to avoid an import cycle).

    Reached through the module object so test monkeypatches on
    ``external_player.<fn>`` are honored and the legacy helpers stay the single
    implementation.
    """
    try:
        from . import external_player as ep
    except ImportError:  # pragma: no cover - bare-name fallback (run as __main__)
        import external_player as ep  # type: ignore[no-redef]
    return ep


def _status(
    media_file: str,
    launch_source: str,
    arch: dict[str, str],
    *,
    session_state: str,
    snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    status: dict[str, Any] = {
        "launch_source": launch_source,
        "architecture_preset": arch["preset"],
        "routing_mode": arch["routing"],
        "monitor_mode": arch["monitor_mode"],
        "media_file": media_file,
        "session_state": session_state,
        "confirmed_playback": False,
        "confirmed_progress": False,
    }
    if snapshot is not None:
        status["confirmed_playback"] = bool(snapshot.get("confirmed_playback"))
        status["confirmed_progress"] = bool(snapshot.get("confirmed_progress"))
        status["oppo_playback_state"] = snapshot.get("oppo_playback_state")
        status["utc_tick_count"] = snapshot.get("utc_tick_count")
        status["stop_reason"] = snapshot.get("stop_reason")
    return status


def _write_status(settings: Settings, status: dict[str, Any]) -> None:
    """Write the status JSON next to the sentinel. Never raises."""
    addon_data = settings.get("addon_data_dir", "")
    if not addon_data:
        return
    path = os.path.join(addon_data, STATUS_FILENAME)
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(status, handle)
    except OSError:
        pass


def _run_svm3_monitor(settings: Settings, ep: Any) -> dict[str, Any] | None:
    """Run the SVM3 monitor. Return its snapshot, or None if it could not connect.

    A None return is the caller's signal to fall back to the legacy hold. The
    previous verbose mode is always restored and the socket closed.
    """
    try:
        from ..oppo.playback_monitor_svm3 import OppoSvm3PlaybackMonitor
    except ImportError:  # pragma: no cover - bare-name fallback (run as __main__)
        from playback_monitor_svm3 import OppoSvm3PlaybackMonitor  # type: ignore[no-redef]

    monitor = OppoSvm3PlaybackMonitor(
        settings.get("oppo_ip", ""),
        settings.get("oppo_port", "23"),
        logger=ep.log,
        full_event_log=settings.get_bool("oppo_svm3_full_event_log", False),
    )
    try:
        monitor.connect()
    except OSError as exc:
        ep.log(f"SVM3 monitor could not connect ({exc}); falling back to legacy hold.")
        return None
    try:
        monitor.query_previous_verbose_mode()
        monitor.enable()
        snapshot = monitor.listen_until_done()
    finally:
        monitor.restore()
        monitor.close()
    ep.log(
        f"SVM3 monitor ended: stop_reason={snapshot.get('stop_reason')} "
        f"confirmed={snapshot.get('confirmed')}"
    )
    return snapshot


def _dispatch_monitor(settings: Settings, ep: Any, arch: dict[str, str]) -> dict[str, Any] | None:
    """Run the configured monitor. Returns the SVM3 snapshot, or None for legacy."""
    if arch["monitor_mode"] == "svm3":
        snapshot = _run_svm3_monitor(settings, ep)
        if snapshot is not None:
            return snapshot
    ep.hold_playback(settings)
    return None


def run_playback_session(
    settings: Settings,
    media_file: str,
    launch_source: str,
    preflight_result: dict[str, object] | None = None,
    *,
    player: Any = None,
) -> int:
    """Run one OPPO playback session. Returns 0 on success, 1 on error.

    ``launch_source`` is ``playercorefactory`` or ``service_interception``; it is
    recorded in the status JSON but does not change the sequence. The session
    sentinel and verbose-mode restore always run in the finally block.

    ``player`` injects the external_player module; it defaults to a lazy import.
    ``main()`` passes its own module so the helpers resolve to the same instance
    when external_player is run directly as ``__main__``.
    """
    ep = player if player is not None else _external_player()
    arch = normalize_architecture(settings)
    _write_status(settings, _status(media_file, launch_source, arch, session_state="starting"))
    rc = 0
    snapshot: dict[str, Any] | None = None
    try:
        ep.mark_session_active(settings)
        if arch["routing"] == "http_handoff":
            ep.fast_start_http(settings, media_file)
        else:
            ep.fast_start(settings, media_file, preflight_result=preflight_result)
        snapshot = _dispatch_monitor(settings, ep, arch)
    except Exception:
        traceback.print_exc()
        rc = 1
    finally:
        try:
            ep.fast_return(settings)
        except Exception:
            traceback.print_exc()
        ep.clear_session_active(settings)
        _write_status(
            settings,
            _status(
                media_file,
                launch_source,
                arch,
                session_state="failed" if rc else "stopped",
                snapshot=snapshot,
            ),
        )
    return rc
