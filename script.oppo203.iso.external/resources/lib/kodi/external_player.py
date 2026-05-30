#!/usr/bin/env python3
"""External-player bridge: hand a 4K disc to the OPPO and hold Kodi's place until it stops.

WHERE THIS FILE SITS
--------------------
This is the load-bearing file of the add-on. When a 4K disc is started in Kodi, this script
is what actually drives the home theatre: it points the TV at the OPPO, (optionally) preps
the audio/video receiver, tells the physical OPPO Blu-ray player to start the disc, then
"holds" Kodi in a busy state until the OPPO reports it has stopped, and finally puts the TV
and receiver back the way they were.

A few terms, defined once here (they recur throughout the file):
  * "external player" -- Kodi does not decode the disc itself; it launches a separate
    program to play it. Here that program is THIS script, which in turn commands a real OPPO
    box over the home network. Kodi just waits for the script to return.
  * playercorefactory.xml -- a Kodi configuration file (written once during setup) that
    tells Kodi "for a file that looks like a 4K disc, launch this script instead of playing
    it yourself." We do not edit it here; we are the script it launches.
  * This add-on does NOT stream, and does NOT call Kodi's setResolvedUrl (the usual way an
    add-on says "here is a video URL, play it"). Nothing is streamed -- a physical disc
    plays in a physical OPPO on the LAN while Kodi merely keeps its playback slot occupied.
  * The codes we send: the OPPO has a plain-text control channel on TCP port 23. We send
    short codes such as #PON (power on), #EJT (eject -- used to wake some clone players),
    #SVM (turn on verbose status messages), and #QPW / #QIS / #QPL (query power / input /
    playback status). Some boxes instead expose an HTTP API on port 436. Other terms:
    AVR = audio/video receiver; ADB = Android Debug Bridge, one way to tell an Android TV to
    switch its input; Wake-on-LAN = a special network packet that powers a sleeping box on.

THE END-TO-END FLOW (what actually happens when a 4K disc is played)
--------------------------------------------------------------------
1. The user plays a disc file (.iso / a BDMV folder / a .mpls playlist) whose *filename*
   contains a 4K tag such as "4K", "UHD", or "2160p".
2. Kodi's own engine (NOT this code) matches that filename against the rule in
   playercorefactory.xml and launches this file as a separate process, roughly:
       external_player.py --addon-data <settings dir> --file "<the disc file>"
   So our only two inputs are a settings directory and the file path. We ASSUME Kodi only
   launches us for files that really are 4K discs -- the matching already happened upstream.
3. main() runs the pipeline (see main() for the exact guarantees):
     a. read_settings(<dir>)     -> load the user's saved configuration.
     b. run_preflight() [opt.]   -> ask the OPPO over TCP whether it is already on and what
                                    input it is using (#QPW / #QIS), if preflight is enabled.
     c. mark_session_active()    -> write a small sentinel file so the rest of the add-on
                                    can tell that an OPPO session is in progress.
     d. fast_start()             -> TV -> AVR -> OPPO, in that order (see fast_start()).
     e. hold_playback()          -> block here, watching, until the OPPO says it stopped
                                    (one of five strategies).
     f. fast_return()            -> stop the OPPO, restore the AVR, switch the TV back.
     g. clear_session_active()   -> delete the sentinel file.
   Steps f and g run inside a finally block, so they happen even if a step above fails.

WHY THE ORDER, AND THE "NON-FATAL" RULE, MATTER
-----------------------------------------------
The TV switch and the AVR prep are deliberately *non-fatal*: if the TV or receiver does not
respond, we log it and carry on, because the one thing that must still happen is starting
(and later stopping) the OPPO and cleaning up the sentinel. A flaky TV must never strand the
system half-up. Watch for that pattern in _safe_tv_switch() and in fast_start()/fast_return().

(The add-on has a second architecture, "service interception" mode, which lives in
service.py. It reaches the exact same fast_start -> hold_playback -> fast_return steps, so
this file is the shared core of both.)
"""

from __future__ import annotations

import argparse
import os
import sys
import threading
import time
import traceback
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Callable, cast

if TYPE_CHECKING:  # pragma: no cover
    from .settings_reader import Settings

# Import shim: when this file is imported as part of the add-on package, the relative
# imports below ("from ..oppo ...") resolve normally. But Kodi can also launch this file as
# a standalone script (its "external player"), in which case Python has no package context
# and those relative imports fail -- so the except branch re-imports the very same names by
# their bare module names instead. Same code, loaded two different ways.
try:
    from ..avr.avr_sequence import post_playback_sequence, pre_playback_sequence
    from ..oppo.oppo_control import (
        get_playback_info,
        http_info_indicates_playing,
        http_info_is_definitive_stop,
        http_status_is_idle,
        query_playback_status,
        run_configured_commands,
        run_preflight,
        run_start,
        tcp_qpl_is_idle,
    )
    from ..tv.tv_control import switch_to_kodi, switch_to_oppo
    from .diagnostic_logging import log_to_xbmc
    from .settings_reader import read_settings
except ImportError:  # pragma: no cover - run as __main__ via runpy / bare-name fallback
    from avr_sequence import post_playback_sequence, pre_playback_sequence  # type: ignore[no-redef]
    from diagnostic_logging import log_to_xbmc  # type: ignore[no-redef]
    from oppo_control import (  # type: ignore[no-redef]
        get_playback_info,
        http_info_indicates_playing,
        http_info_is_definitive_stop,
        http_status_is_idle,
        query_playback_status,
        run_configured_commands,
        run_preflight,
        run_start,
        tcp_qpl_is_idle,
    )
    from settings_reader import read_settings  # type: ignore[no-redef]
    from tv_control import switch_to_kodi, switch_to_oppo  # type: ignore[no-redef]


def log(message: str) -> None:
    """Write one line to Kodi's log under the "player" category.

    A thin wrapper so the rest of this file can just call log("..."). Side effect: appends to
    Kodi's log file. It never raises, so logging can never interrupt playback.
    """
    log_to_xbmc(None, "player", message)


def session_file(settings: Settings) -> str:
    """Return the full path of the "a session is active" sentinel file.

    The sentinel is just a marker file named "oppo203iso-active" kept in the add-on's data
    directory. Returns "" (empty string) if no data directory is configured, which the
    callers below treat as "skip the sentinel entirely".
    """
    return os.path.join(settings.get("addon_data_dir", ""), "oppo203iso-active")


def mark_session_active(settings: Settings) -> None:
    """Create the sentinel file that means "an OPPO playback session is in progress".

    Other parts of the add-on check for this file so they do not step on an active session.
    Side effect: writes a file to disk (its contents are just the current timestamp). Does
    nothing if no data directory is configured.
    """
    path = session_file(settings)
    if not path:
        return
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(str(time.time()))


def clear_session_active(settings: Settings) -> None:
    """Delete the sentinel file, marking the session finished.

    Side effect: removes the file written by mark_session_active(). Safe to call even if the
    file was never created. main() calls this last, inside a finally block, so the marker is
    cleared even when playback fails partway through.
    """
    path = session_file(settings)
    if path and os.path.exists(path):
        os.remove(path)


def run_parallel(tasks: Iterable[tuple[str, Callable[[], object]]]) -> None:
    """Run several named tasks at the same time (one thread each) and wait for all of them.

    Each task is a (name, function) pair. Every function runs on its own background thread,
    and this call blocks until they all finish. If one or more raise, every error is logged
    and the FIRST exception is then re-raised so the caller still sees a failure.

    Takes: an iterable of (name, zero-argument callable) pairs.
    Can go wrong: whatever the task functions themselves do; their exceptions are captured
    per task rather than crashing the other threads.
    """
    errors: list[tuple[str, Exception, str]] = []

    def runner(name: str, func: Callable[[], object]) -> None:
        try:
            func()
        except Exception as exc:
            errors.append((name, exc, traceback.format_exc()))

    threads = [
        threading.Thread(target=runner, args=(name, func), daemon=True) for name, func in tasks
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    if errors:
        for name, exc, tb in errors:
            log(f"{name} failed: {exc}")
            log_to_xbmc(None, "player", tb)
        raise errors[0][1]


def start_oppo_after_optional_delay(
    settings: Settings, media_file: str, preflight_result: dict[str, object] | None = None
) -> None:
    """Wait an optional configured delay, then tell the OPPO to start playing.

    Some setups need a short pause (for example, to let the TV finish switching inputs)
    before the player is woken. "startup_delay" is a number of SECONDS (0 = no wait); a
    larger value simply delays playback. Side effects: may sleep, then sends start commands
    to the OPPO over the network via run_start(). preflight_result, when present, lets
    run_start() reuse what main()'s preflight step already learned (power/input) instead of
    re-asking the player.
    """
    startup_delay = int(settings.get("startup_delay", "0"))
    if startup_delay > 0:
        log(f"Waiting {startup_delay} second(s) before starting Oppo.")
        time.sleep(startup_delay)
    log(f"Starting Oppo with mode: {settings.get('oppo_start_mode', 'tcp_commands')}.")
    run_start(settings, media_file, preflight_result=preflight_result)


def tv_switching_enabled(settings: Settings) -> bool:
    """Return True when MVP TV input switching should run.

    The v2 MVP keeps TCL/Android TV switching optional and settings-controlled.
    `tv_switching_enabled=false` is the explicit no-op path for users who do
    not want ADB/TV control during the External Player flow. Empty/disabled TV
    backend values are also treated as disabled for migration safety.
    """
    backend = str(settings.get("tv_backend", "adb") or "").strip().lower()
    if backend in ("", "none", "disabled", "off"):
        return False
    return settings.get_bool("tv_switching_enabled", True)


def _safe_tv_switch(settings: Settings, target: str) -> str | dict[str, object] | None:
    """Switch TV input if enabled, but never corrupt playback cleanup.

    ADB and TV-control failures are logged as non-fatal because the MVP
    requirement is that TV switching failures must not prevent OPPO startup,
    stop commands, or session-sentinel cleanup.
    """
    if not tv_switching_enabled(settings):
        log(f"TV switching disabled; skipping switch to {target} input.")
        return None
    try:
        if target == "oppo":
            log("Switching TV to Oppo input.")
            return switch_to_oppo(cast("dict[str, Any]", settings))
        log("Switching TV back to Kodi input.")
        return switch_to_kodi(cast("dict[str, Any]", settings))
    except Exception as exc:
        log(f"TV switch to {target} failed (non-fatal): {exc}")
        return None


def fast_start(
    settings: Settings, media_file: str, preflight_result: dict[str, object] | None = None
) -> None:
    """Bring the home theatre up for playback, in a deliberate, failure-tolerant order.

    The order is TV -> AVR -> OPPO:
      1. _safe_tv_switch(..., "oppo")          -- point the TV at the OPPO's HDMI input.
      2. pre_playback_sequence(...)            -- prep the audio/video receiver (off by
                                                  default; a warning here is non-fatal).
      3. start_oppo_after_optional_delay(...)  -- wake the OPPO and start the disc.
    Steps 1 and 2 are NON-FATAL by design: a TV or receiver that does not answer is logged
    and skipped, so it can never block the OPPO from starting. Side effects: talks to the
    TV, the receiver, and the OPPO over the network. The handoff to the OPPO assumes
    media_file is exactly the path Kodi gave us on the command line.
    """
    # v2 MVP Slice 3: make startup order deterministic and safe.
    # TV switching is attempted before OPPO/external playback handoff, but TV
    # failures are non-fatal so they do not corrupt playback or cleanup.
    if settings.get_bool("fast_changeover", True):
        log("Fast changeover requested; v2 MVP uses safe TV-first startup order.")
    _safe_tv_switch(settings, "oppo")
    avr_result = pre_playback_sequence(settings)
    if not avr_result.ok and not avr_result.skipped:
        log(f"AVR pre-playback sequence warning (non-fatal): {avr_result.warnings}")
    start_oppo_after_optional_delay(settings, media_file, preflight_result)


def fast_return(settings: Settings) -> None:
    """Tear the session down and put everything back the way it was.

    Runs after playback -- main() calls it inside a finally block, so it runs even on error:
      1. Send the OPPO its configured stop commands.
      2. Restore the audio/video receiver (off by default).
      3. If "switch_back_on_exit" is set, point the TV back at Kodi's input.
    The TV and AVR steps are non-fatal, the same as in fast_start(). Side effects: network
    commands to the OPPO, the receiver, and the TV.
    """
    log("Sending Oppo stop commands.")
    run_configured_commands(settings, "oppo_stop_commands")
    avr_result = post_playback_sequence(settings)
    if not avr_result.ok and not avr_result.skipped:
        log(f"AVR post-playback sequence warning (non-fatal): {avr_result.warnings}")
    if settings.get_bool("switch_back_on_exit", True):
        _safe_tv_switch(settings, "kodi")


def hold_playback(settings: Settings) -> None:
    """Block here, watching, until the OPPO reports it has stopped playing.

    Why this exists: Kodi believes IT is playing something (it launched us as its "player"),
    so we must not return until the real disc actually finishes. Returning early would make
    Kodi think playback ended and move on while the disc is still playing. This function is
    that wait.

    The "hold_mode" setting picks one of five strategies for answering "has it stopped yet?":
      * http_poll     -- ask the OPPO over its HTTP API every few seconds and read its status.
      * tcp_qpl_poll  -- ask over TCP using the #QPL ("query playback") code instead.
      * verbose_push  -- open a TCP connection and LISTEN for the OPPO to push status updates
                         (@UPW / @UPL); falls back to tcp_qpl_poll if that connection fails.
      * manual_file   -- wait until the user (or a script) creates a chosen "stop" file.
      * fixed_timeout -- the default: simply sleep for a fixed number of minutes.
    Every polling mode also carries a safety timeout, so a missed "stopped" signal can never
    hold Kodi forever. Side effects: repeated network queries to the OPPO and, in every mode,
    blocking (sleeping) for as long as the disc plays.

    Reading the numbers below: intervals are in SECONDS and the large timeouts are in
    MINUTES. "idle confirmations" means the OPPO must look stopped N times in a row before we
    believe it, so a single momentary blip does not end playback prematurely.
    """
    mode = settings.get("hold_mode", "fixed_timeout")

    if mode == "http_poll":
        # "Trick-play" below = fast-forward, rewind, pause, or sitting in a disc menu. During
        # those the OPPO can briefly report "idle/stopped" even though the user is still
        # watching, so after any real play activity we ignore idle readings for a few seconds
        # (the "suppress window") to avoid ending the hold too early.
        interval = max(1, int(settings.get("http_poll_interval", "5")))
        timeout = max(1, int(settings.get("http_poll_timeout_minutes", "240"))) * 60
        confirmations_needed = max(1, int(settings.get("http_poll_idle_confirmations", "2")))
        # v0.9.0: trick-play suppression window (default 45s, from OppofromAVS reference)
        trickplay_suppress = max(0, int(settings.get("trickplay_suppress_seconds", "45")))
        started_at = time.time()
        idle_confirmations = 0
        ignore_until = 0.0  # v0.9.0: ignore idle readings until this time
        log(
            f"HTTP polling hold active: interval={interval}s, timeout={timeout}s, idle confirmations={confirmations_needed}, "
            f"trickplay_suppress={trickplay_suppress}s."
        )
        while time.time() - started_at < timeout:
            try:
                info = get_playback_info(settings)
                status = ""
                if isinstance(info, dict):
                    from oppo_control import _info_containers

                    for container in _info_containers(info):
                        if isinstance(container, dict):
                            for key in ("e_play_status", "play_status", "status", "state"):
                                val = container.get(key)
                                if val is not None:
                                    status = str(val).strip().upper()
                                    break
                        if status:
                            break

                now = time.time()
                log(f"Oppo HTTP playback status: {status or 'unknown'}")

                # v0.9.0: errcode1 == -5 is the official clean-stop signal; end immediately.
                if http_info_is_definitive_stop(info):
                    log("Oppo returned errcode1=-5 (definitive stop). Ending hold immediately.")
                    return

                # v0.9.0: actively playing or trick-play active -- reset idle counter
                # and extend the suppress window.
                if http_info_indicates_playing(info):
                    if idle_confirmations > 0:
                        log("Oppo is playing/trick-playing; resetting idle counter.")
                    idle_confirmations = 0
                    ignore_until = now + trickplay_suppress
                elif http_status_is_idle(status):
                    # Only count idle confirmations after the suppress window expires.
                    if now >= ignore_until:
                        idle_confirmations += 1
                        log(f"Idle confirmation {idle_confirmations}/{confirmations_needed}.")
                        if idle_confirmations >= confirmations_needed:
                            log("Oppo playback appears idle/stopped (HTTP). Ending hold.")
                            return
                    else:
                        log(
                            f"Idle status received but inside trickplay suppress window "
                            f"({ignore_until - now:.1f}s remaining); ignoring."
                        )
                else:
                    # Unknown/ambiguous status -- treat conservatively as non-idle.
                    idle_confirmations = 0
            except Exception as exc:
                log(f"Oppo HTTP status poll failed: {exc}")
                idle_confirmations = 0
            time.sleep(interval)
        log("HTTP polling hold timed out. Ending hold.")
        return

    if mode == "tcp_qpl_poll":
        # v0.8.0: Poll #QPL over TCP and stop when status is idle/stopped
        host = settings["oppo_ip"]
        port = int(settings.get("oppo_port", "23"))
        timeout_secs = float(settings.get("oppo_socket_timeout", "3.0"))
        interval = max(1, int(settings.get("qpl_poll_interval", "3")))
        max_seconds = max(1, int(settings.get("qpl_poll_timeout_minutes", "240"))) * 60
        confirmations_needed = max(1, int(settings.get("qpl_poll_idle_confirmations", "2")))
        started_at = time.time()
        idle_confirmations = 0
        log(
            f"TCP QPL polling hold active: interval={interval}s, timeout={max_seconds}s, idle confirmations={confirmations_needed}."
        )
        while time.time() - started_at < max_seconds:
            try:
                status = query_playback_status(host, port, timeout=timeout_secs)
                log(f"Oppo QPL status: {status or 'timeout/no-response'}")
                if tcp_qpl_is_idle(status):
                    idle_confirmations += 1
                    if idle_confirmations >= confirmations_needed:
                        log("Oppo QPL status indicates idle/stopped. Ending hold.")
                        return
                else:
                    idle_confirmations = 0
            except Exception as exc:
                log(f"Oppo TCP QPL poll failed: {exc}")
                idle_confirmations = 0
            time.sleep(interval)
        log("TCP QPL polling hold timed out. Ending hold.")
        return

    if mode == "verbose_push":
        # v0.9.0: Persistent TCP verbose-push hold mode.
        # Uses oppo_tcp_client.py to listen for @UPW/@UPL push messages.
        # Falls back to tcp_qpl_poll on connection failure.
        vp_timeout = (
            max(
                1,
                int(
                    settings.get(
                        "verbose_push_timeout_minutes",
                        settings.get("qpl_poll_timeout_minutes", "240"),
                    )
                ),
            )
            * 60
        )
        log(f"Verbose push hold mode: timeout={vp_timeout}s.")
        try:
            from oppo_tcp_client import OppoTcpClient  # noqa: PLC0415

            host = settings["oppo_ip"]
            port = int(settings.get("oppo_port", "23"))
            client = OppoTcpClient(host, port)
            log("Starting verbose TCP push listener.")
            stopped = client.wait_for_stop(timeout=vp_timeout)
            if stopped:
                log("Verbose push: stop condition received. Ending hold.")
            else:
                log("Verbose push: timed out. Ending hold.")
            return
        except Exception as exc:
            log(f"Verbose push TCP client failed ({exc}); falling back to tcp_qpl_poll.")
            # Fall through to tcp_qpl_poll logic below by modifying mode
            mode = "tcp_qpl_poll"

    if mode == "manual_file":
        stop_file = settings.get("manual_stop_file", "/tmp/oppo203_iso_stop")
        log(f"Manual-file hold active. Create this file to stop: {stop_file}")
        while not os.path.exists(stop_file):
            time.sleep(2)
        try:
            os.remove(stop_file)
        except OSError:
            pass
        return

    minutes = int(settings.get("fixed_timeout_minutes", "180"))
    seconds = max(1, minutes * 60)
    log(f"Fixed-timeout hold active for {minutes} minute(s).")
    time.sleep(seconds)


def main() -> int:
    """Entry point: run the whole start -> hold -> stop pipeline for one disc, safely.

    Kodi launches this with two command-line arguments: --addon-data (the settings folder)
    and --file (the disc to play). It then:
      1. Loads settings and records the data directory on them.
      2. Optionally runs preflight queries (#QPW power, #QIS input) if enabled in settings.
      3. Inside a try/finally: marks the session active, runs fast_start(), then
         hold_playback() (which blocks until the disc stops).
      4. NO MATTER WHAT (the finally block): runs fast_return() to stop the OPPO and restore
         the TV/AVR, then clears the session sentinel.
    Returns 0 on success, or 1 if start/hold raised. The try/finally is the key safety net:
    even if startup or the hold crashes, the OPPO is still told to stop and the sentinel is
    still removed, so the system is never left half-up. Side effects: everything downstream
    -- network commands to the TV/AVR/OPPO, a sentinel file written then deleted, and
    blocking for the full duration of the disc.
    """
    parser = argparse.ArgumentParser(
        description="Kodi external-player wrapper for Oppo UDP-203 ISO playback."
    )
    parser.add_argument(
        "--addon-data", required=True, help="Kodi addon_data directory for this add-on."
    )
    parser.add_argument("--file", required=True, help="ISO file path passed by Kodi.")
    args = parser.parse_args()

    settings = read_settings(args.addon_data)
    settings.data["addon_data_dir"] = args.addon_data
    log(f"Requested ISO: {args.file}")

    # v0.8.0: Optional preflight queries
    preflight_result = None
    if settings.get_bool("oppo_preflight_enabled", False):
        log("Running preflight queries (#QPW, #QIS).")
        try:
            preflight_result = run_preflight(settings)
            log(
                "Preflight result: power={}, input={}, already_on={}.".format(
                    preflight_result.get("power_status"),
                    preflight_result.get("input_source"),
                    preflight_result.get("already_on"),
                )
            )
        except Exception as exc:
            log(f"Preflight failed (non-fatal): {exc}")

    try:
        mark_session_active(settings)
        fast_start(settings, args.file, preflight_result=preflight_result)
        hold_playback(settings)

    except Exception:
        traceback.print_exc()
        return 1

    finally:
        try:
            fast_return(settings)
        except Exception:
            traceback.print_exc()
        clear_session_active(settings)

    return 0


if __name__ == "__main__":
    sys.exit(main())
