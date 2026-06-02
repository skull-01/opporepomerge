#!/usr/bin/env python3
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


# Consecutive OPPO poll failures (connection refused / unreachable) that end a
# hold instead of running to the full timeout when the player drops off the
# network mid-playback. A graceful no-response (recv timeout) does not count.
MAX_CONSECUTIVE_POLL_FAILURES = 5


def log(message: str) -> None:
    log_to_xbmc(None, "player", message)


def session_file(settings: Settings) -> str:
    return os.path.join(settings.get("addon_data_dir", ""), "oppo203iso-active")


def mark_session_active(settings: Settings) -> None:
    path = session_file(settings)
    if not path:
        return
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(str(time.time()))


def clear_session_active(settings: Settings) -> None:
    path = session_file(settings)
    if path and os.path.exists(path):
        os.remove(path)


def run_parallel(tasks: Iterable[tuple[str, Callable[[], object]]]) -> None:
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


def _oppo_control_module() -> Any:
    """Return the oppo_control module (package import with a bare-name fallback)."""
    try:
        from ..oppo import oppo_control as oc
    except ImportError:  # pragma: no cover - bare-name fallback (run as __main__)
        import oppo_control as oc  # type: ignore[no-redef]
    return oc


def _http_best_effort(action: Callable[[], Any], label: str) -> None:
    """Run one best-effort HTTP orchestration step; log and swallow transport failures so the
    overall launch never crashes on an enrichment step the player may not support."""
    try:
        action()
    except (RuntimeError, OSError) as exc:
        log(f"OPPO HTTP {label} step skipped (non-fatal): {exc}")


def _parse_network_share(media_file: str) -> tuple[str, str, str] | None:
    """Return (scheme, server, share) for an ``smb://server/share/...`` or ``nfs://`` media URL,
    or None when the path is not a network URL the player would need to mount."""
    text = str(media_file).replace("\\", "/")
    for scheme in ("smb", "nfs"):
        prefix = f"{scheme}://"
        if text.lower().startswith(prefix):
            parts = text[len(prefix) :].split("/", 2)
            if len(parts) >= 2 and parts[0] and parts[1]:
                return scheme, parts[0], parts[1]
    return None


def _http_ensure_share_mounted(oc: Any, settings: Settings, media_file: str) -> None:
    """Best-effort: ensure the media's network share is mounted on the player before play.

    Server/share are parsed from the media path; non-network paths are skipped. Every step is
    non-fatal -- a player with the share already mounted (the wizard's prerequisite) is
    unaffected, and a player that does not expose the mount endpoints degrades silently."""
    parsed = _parse_network_share(media_file)
    if parsed is None:
        return
    scheme, server, share = parsed
    user = settings.get("oppo_http_nas_user", "")
    password = settings.get("oppo_http_nas_password", "")

    def mount() -> None:
        if scheme == "nfs" or oc.detect_nfs(settings):
            oc.login_nfs(settings, server)
            oc.mount_nfs(settings, server, share)
        else:
            oc.login_smb(settings, server, user, password)
            oc.mount_smb(settings, server, share, user, password)

    _http_best_effort(mount, f"mount {scheme}://{server}/{share}")


def _http_play_disc_aware(oc: Any, settings: Settings, media_file: str) -> str:
    """Hand the player the right path for the media's disc type. A BDMV folder gets a best-effort
    checkfolderhasBDMV probe (logged); an ISO gets a one-shot auto-heal. The play itself stays
    the proven play_media_http_api, so the disc-awareness only adds a probe + the ISO resend."""
    try:
        from . import disc_classification as dc
    except ImportError:  # pragma: no cover - bare-name fallback (run as __main__)
        import disc_classification as dc  # type: ignore[no-redef]

    if dc.is_bdmv_navigation_path(media_file):
        _http_best_effort(
            lambda: log(
                f"OPPO BDMV folder check: has_bdmv={oc.check_folder_has_bdmv(settings, media_file)}"
            ),
            "checkfolderhasBDMV",
        )
        return cast("str", oc.play_media_http_api(settings, media_file))

    reply = cast("str", oc.play_media_http_api(settings, media_file))
    if dc.extension(media_file) == ".iso" and settings.get_bool("oppo_http_iso_autoheal", True):
        _http_autoheal_iso(oc, settings, media_file)
    return reply


def _http_autoheal_iso(oc: Any, settings: Settings, media_file: str) -> None:
    """One-shot ISO auto-heal: if the player is not confirmed playing after the configured grace
    period, resend the ISO once (stop, then play). Some players drop the first ISO mount. The
    whole step is non-fatal and skipped when the player cannot be queried."""
    delay = max(1, int(settings.get("oppo_http_iso_autoheal_after_seconds", "20")))
    time.sleep(delay)
    try:
        if oc.global_info_is_playing(oc.get_global_info(settings)):
            return
    except (RuntimeError, OSError):
        return  # cannot confirm -> do not poke a possibly-healthy session
    log("OPPO ISO not confirmed playing after grace period; auto-healing (resend once).")
    _http_best_effort(lambda: oc.send_remote_key_http(settings, "STP"), "iso-autoheal-stop")
    _http_best_effort(lambda: oc.play_media_http_api(settings, media_file), "iso-autoheal-replay")


def _http_log_confirmation(oc: Any, settings: Settings) -> None:
    """Best-effort: log whether getglobalinfo reports playback after the launch."""

    def check() -> None:
        playing = oc.global_info_is_playing(oc.get_global_info(settings))
        log(f"OPPO HTTP confirm: getglobalinfo playing={playing}")

    _http_best_effort(check, "getglobalinfo confirm")


def _start_oppo_http(settings: Settings, media_file: str) -> None:
    """Pure-HTTP launch orchestration (Xnoppo V3): wake -> signin -> best-effort mount ->
    disc-aware play (+ one-shot ISO auto-heal) -> confirm.

    Only ``activate -> signin -> play`` is required; every other step (the PON wake, the share
    mount, the BDMV probe, the auto-heal, the getglobalinfo confirm) is best-effort and non-fatal,
    so a player that does not speak the newer endpoints degrades to exactly today's http_handoff
    behaviour. The HTTP API is community-reverse-engineered -- not an official OPPO protocol claim,
    and not hardware-validated.
    """
    oc = _oppo_control_module()
    startup_delay = int(settings.get("startup_delay", "0"))
    if startup_delay > 0:
        log(f"Waiting {startup_delay} second(s) before HTTP handoff.")
        time.sleep(startup_delay)
    try:
        oc.activate_http_api(settings)
        _http_best_effort(lambda: oc.send_remote_key_http(settings, "PON"), "wake")
        oc.signin_http_api(settings)
        _http_ensure_share_mounted(oc, settings, media_file)
        reply = _http_play_disc_aware(oc, settings, media_file)
        log(f"OPPO HTTP handoff launched: {reply!r}")
        _http_log_confirmation(oc, settings)
    except Exception as exc:
        log(f"OPPO HTTP handoff failed (non-fatal): {exc}")


def fast_start_http(settings: Settings, media_file: str) -> None:
    """HTTP-handoff launch: TV switch + AVR pre-sequence, then the community OPPO
    HTTP file launch instead of the TCP/disc start. The monitor axis (legacy/svm3)
    confirms playback afterwards, exactly as for the other routings."""
    if settings.get_bool("fast_changeover", True):
        log("Fast changeover requested; v2 MVP uses safe TV-first startup order.")
    _safe_tv_switch(settings, "oppo")
    avr_result = pre_playback_sequence(settings)
    if not avr_result.ok and not avr_result.skipped:
        log(f"AVR pre-playback sequence warning (non-fatal): {avr_result.warnings}")
    _start_oppo_http(settings, media_file)


def fast_return(settings: Settings) -> None:
    log("Sending Oppo stop commands.")
    run_configured_commands(settings, "oppo_stop_commands")
    avr_result = post_playback_sequence(settings)
    if not avr_result.ok and not avr_result.skipped:
        log(f"AVR post-playback sequence warning (non-fatal): {avr_result.warnings}")
    if settings.get_bool("switch_back_on_exit", True):
        _safe_tv_switch(settings, "kodi")


def _hold_tcp_qpl_poll(settings: Settings) -> None:
    # Poll #QPL over TCP and end the hold when the player reports idle/stopped.
    host = settings["oppo_ip"]
    port = int(settings.get("oppo_port", "23"))
    timeout_secs = float(settings.get("oppo_socket_timeout", "3.0"))
    interval = max(1, int(settings.get("qpl_poll_interval", "3")))
    max_seconds = max(1, int(settings.get("qpl_poll_timeout_minutes", "240"))) * 60
    confirmations_needed = max(1, int(settings.get("qpl_poll_idle_confirmations", "2")))
    started_at = time.time()
    idle_confirmations = 0
    consecutive_failures = 0
    log(
        f"TCP QPL polling hold active: interval={interval}s, timeout={max_seconds}s, idle confirmations={confirmations_needed}."
    )
    while time.time() - started_at < max_seconds:
        try:
            status = query_playback_status(host, port, timeout=timeout_secs)
            consecutive_failures = 0
            log(f"Oppo QPL status: {status or 'timeout/no-response'}")
            if tcp_qpl_is_idle(status):
                idle_confirmations += 1
                if idle_confirmations >= confirmations_needed:
                    log("Oppo QPL status indicates idle/stopped. Ending hold.")
                    return
            else:
                idle_confirmations = 0
        except Exception as exc:
            consecutive_failures += 1
            log(
                f"Oppo TCP QPL poll failed "
                f"({consecutive_failures}/{MAX_CONSECUTIVE_POLL_FAILURES}): {exc}"
            )
            idle_confirmations = 0
            if consecutive_failures >= MAX_CONSECUTIVE_POLL_FAILURES:
                log("Oppo unreachable for too many consecutive QPL polls. Ending hold.")
                return
        time.sleep(interval)
    log("TCP QPL polling hold timed out. Ending hold.")


def hold_playback(settings: Settings) -> None:
    mode = settings.get("hold_mode", "fixed_timeout")

    if mode == "http_poll":
        interval = max(1, int(settings.get("http_poll_interval", "5")))
        timeout = max(1, int(settings.get("http_poll_timeout_minutes", "240"))) * 60
        confirmations_needed = max(1, int(settings.get("http_poll_idle_confirmations", "2")))
        # v0.9.0: trick-play suppression window (default 45s, from OppofromAVS reference)
        trickplay_suppress = max(0, int(settings.get("trickplay_suppress_seconds", "45")))
        started_at = time.time()
        idle_confirmations = 0
        consecutive_failures = 0
        ignore_until = 0.0  # v0.9.0: ignore idle readings until this time
        log(
            f"HTTP polling hold active: interval={interval}s, timeout={timeout}s, idle confirmations={confirmations_needed}, "
            f"trickplay_suppress={trickplay_suppress}s."
        )
        while time.time() - started_at < timeout:
            try:
                info = get_playback_info(settings)
                consecutive_failures = 0
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
                consecutive_failures += 1
                log(
                    f"Oppo HTTP status poll failed "
                    f"({consecutive_failures}/{MAX_CONSECUTIVE_POLL_FAILURES}): {exc}"
                )
                idle_confirmations = 0
                if consecutive_failures >= MAX_CONSECUTIVE_POLL_FAILURES:
                    log("Oppo unreachable for too many consecutive HTTP polls. Ending hold.")
                    return
            time.sleep(interval)
        log("HTTP polling hold timed out. Ending hold.")
        return

    if mode == "tcp_qpl_poll":
        _hold_tcp_qpl_poll(settings)
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
            _hold_tcp_qpl_poll(settings)
            return

    if mode == "manual_file":
        stop_file = settings.get("manual_stop_file", "/tmp/oppo203_iso_stop")
        # Bound the otherwise-unbounded wait with the fixed-timeout ceiling so a
        # stop file that never appears cannot pin Kodi indefinitely.
        ceiling_minutes = int(settings.get("fixed_timeout_minutes", "180"))
        deadline = time.time() + max(1, ceiling_minutes * 60)
        log(f"Manual-file hold active. Create this file to stop: {stop_file}")
        while not os.path.exists(stop_file):
            if time.time() >= deadline:
                log(
                    f"Manual-file hold reached the {ceiling_minutes}-minute ceiling "
                    f"without a stop file. Ending hold."
                )
                return
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
        from .playback_session import run_playback_session
    except ImportError:  # pragma: no cover - bare-name fallback (run as __main__)
        from playback_session import run_playback_session  # type: ignore[no-redef]

    return run_playback_session(
        settings,
        args.file,
        launch_source="playercorefactory",
        preflight_result=preflight_result,
        player=sys.modules[__name__],
    )


if __name__ == "__main__":
    sys.exit(main())
