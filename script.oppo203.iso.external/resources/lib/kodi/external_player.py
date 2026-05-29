#!/usr/bin/env python3
import argparse
import os
import sys
import threading
import time
import traceback

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
    from avr_sequence import post_playback_sequence, pre_playback_sequence
    from diagnostic_logging import log_to_xbmc
    from oppo_control import (
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
    from settings_reader import read_settings
    from tv_control import switch_to_kodi, switch_to_oppo


def log(message):
    log_to_xbmc(None, "player", message)


def session_file(settings):
    return os.path.join(settings.get("addon_data_dir", ""), "oppo203iso-active")


def mark_session_active(settings):
    path = session_file(settings)
    if not path:
        return
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(str(time.time()))


def clear_session_active(settings):
    path = session_file(settings)
    if path and os.path.exists(path):
        os.remove(path)


def run_parallel(tasks):
    errors = []

    def runner(name, func):
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


def start_oppo_after_optional_delay(settings, media_file, preflight_result=None):
    startup_delay = int(settings.get("startup_delay", "0"))
    if startup_delay > 0:
        log(f"Waiting {startup_delay} second(s) before starting Oppo.")
        time.sleep(startup_delay)
    log(f"Starting Oppo with mode: {settings.get('oppo_start_mode', 'tcp_commands')}.")
    run_start(settings, media_file, preflight_result=preflight_result)


def tv_switching_enabled(settings):
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


def _safe_tv_switch(settings, target):
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
            return switch_to_oppo(settings)
        log("Switching TV back to Kodi input.")
        return switch_to_kodi(settings)
    except Exception as exc:
        log(f"TV switch to {target} failed (non-fatal): {exc}")
        return None


def fast_start(settings, media_file, preflight_result=None):
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


def fast_return(settings):
    log("Sending Oppo stop commands.")
    run_configured_commands(settings, "oppo_stop_commands")
    avr_result = post_playback_sequence(settings)
    if not avr_result.ok and not avr_result.skipped:
        log(f"AVR post-playback sequence warning (non-fatal): {avr_result.warnings}")
    if settings.get_bool("switch_back_on_exit", True):
        _safe_tv_switch(settings, "kodi")


def hold_playback(settings):
    mode = settings.get("hold_mode", "fixed_timeout")

    if mode == "http_poll":
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


def main():
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
