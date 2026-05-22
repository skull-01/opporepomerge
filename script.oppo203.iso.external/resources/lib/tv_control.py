import json
import shlex
import subprocess
import urllib.error
import urllib.request

from adb_control import switch_input as adb_switch_input
from roku_ecp_control import switch_input as roku_switch_input

try:
    from smartthings_control import switch_input as smartthings_switch_input
    from smartthings_control import validation_metadata as smartthings_validation_metadata
except ImportError:  # package import compatibility
    from .smartthings_control import switch_input as smartthings_switch_input  # type: ignore
    from .smartthings_control import validation_metadata as smartthings_validation_metadata

try:
    from .tv_backends import backend_target_setting, is_supported_backend, normalize_backend_id
except ImportError:  # top-level/audit import compatibility
    from tv_backends import (  # type: ignore
        backend_target_setting,
        is_supported_backend,
        normalize_backend_id,
    )


class TVControlError(RuntimeError):
    pass


def _run_external(command, settings, timeout=20):
    command = (command or "").strip()
    if not command:
        raise TVControlError("External TV command is empty.")

    formatted = command.format(tv_ip=settings.get("tv_ip", ""))
    proc = subprocess.run(
        shlex.split(formatted),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        raise TVControlError(
            f"TV command failed: {formatted}\nstdout: {proc.stdout.strip()}\nstderr: {proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def _sony_set_hdmi(settings, port):
    tv_ip = settings["tv_ip"]
    psk = settings.get("sony_psk", "")
    if not psk:
        raise TVControlError("Sony Bravia PSK is required for sony_bravia backend.")

    payload = {
        "method": "setPlayContent",
        "version": "1.0",
        "id": 1,
        "params": [{"uri": f"extInput:hdmi?port={int(port)}"}],
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"http://{tv_ip}/sony/avContent",
        data=body,
        headers={
            "Content-Type": "application/json; charset=UTF-8",
            "X-Auth-PSK": psk,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            if response.status >= 400:
                raise TVControlError(
                    f"Sony Bravia API returned HTTP {response.status}: {response_body}"
                )
            return response_body
    except urllib.error.URLError as exc:
        raise TVControlError(f"Sony Bravia API request failed: {exc}") from exc


def _switch(settings, target):
    backend = normalize_backend_id(settings.get("tv_backend", "adb"))
    if not is_supported_backend(backend):
        raise TVControlError(f"Unsupported TV backend: {backend}")

    if backend == "adb":
        key = backend_target_setting(backend, target) or (
            "oppo_input_adb_shell" if target == "oppo" else "kodi_input_adb_shell"
        )
        return adb_switch_input(settings, settings[key])

    if backend == "sony_bravia":
        key = backend_target_setting(backend, target) or (
            "sony_oppo_hdmi_port" if target == "oppo" else "sony_kodi_hdmi_port"
        )
        return _sony_set_hdmi(settings, settings.get(key, "1"))

    if backend == "lg_command":
        key = backend_target_setting(backend, target) or (
            "lg_oppo_command" if target == "oppo" else "lg_kodi_command"
        )
        return _run_external(settings.get(key, ""), settings)

    if backend == "samsung_command":
        key = backend_target_setting(backend, target) or (
            "samsung_oppo_command" if target == "oppo" else "samsung_kodi_command"
        )
        return _run_external(settings.get(key, ""), settings)

    if backend == "custom_command":
        key = backend_target_setting(backend, target) or (
            "custom_oppo_command" if target == "oppo" else "custom_kodi_command"
        )
        return _run_external(settings.get(key, ""), settings)

    if backend == "roku_ecp":
        key = backend_target_setting(backend, target) or (
            "roku_oppo_key" if target == "oppo" else "roku_kodi_key"
        )
        return roku_switch_input(settings, settings.get(key, ""))

    if backend == "smartthings":
        key = backend_target_setting(backend, target) or (
            "smartthings_oppo_input_id" if target == "oppo" else "smartthings_kodi_input_id"
        )
        metadata = smartthings_validation_metadata(settings)
        if not metadata.get("acknowledged"):
            return smartthings_switch_input(settings, settings.get(key, ""))
        return smartthings_switch_input(settings, settings.get(key, ""))

    raise TVControlError(f"Unsupported TV backend: {backend}")


def selected_backend_id(settings):
    """Return the normalized selected TV backend without performing IO."""
    return normalize_backend_id(settings.get("tv_backend", "adb"))


def switch_to_oppo(settings):
    return _switch(settings, "oppo")


def switch_to_kodi(settings):
    return _switch(settings, "kodi")
