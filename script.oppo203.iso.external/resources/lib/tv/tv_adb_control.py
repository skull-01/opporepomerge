from __future__ import annotations

import shlex
import subprocess
from collections.abc import Callable
from typing import Any


class ADBError(RuntimeError):
    pass


def _run(args: list[str], timeout: int = 15, runner: Callable[..., Any] | None = None) -> str:
    """Run an adb command.

    `runner` is an injectable subprocess-compatible callable used by tests so
    MVP Slice 3 never requires a real TV or real adb binary.
    """
    if runner is None:
        runner = subprocess.run
    proc = runner(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        raise ADBError(
            "ADB command failed: {}\nstdout: {}\nstderr: {}".format(
                " ".join(shlex.quote(a) for a in args),
                str(getattr(proc, "stdout", "")).strip(),
                str(getattr(proc, "stderr", "")).strip(),
            )
        )
    return str(getattr(proc, "stdout", "")).strip()


def adb_connect(
    adb_path: str, host: str, port: int, runner: Callable[..., Any] | None = None
) -> str:
    return _run([adb_path, "connect", f"{host}:{port}"], runner=runner)


def adb_shell(
    adb_path: str,
    host: str,
    port: int,
    command: str,
    runner: Callable[..., Any] | None = None,
) -> str:
    target = f"{host}:{port}"
    return _run([adb_path, "-s", target, "shell"] + shlex.split(command), runner=runner)


def switch_input(
    settings: Any, shell_command: str, runner: Callable[..., Any] | None = None
) -> str:
    adb_path = settings.get("adb_path", "adb")
    tv_ip = settings["tv_ip"]
    tv_port = int(settings.get("tv_adb_port", "5555"))
    injected = settings.get("_adb_runner", None)
    if injected is not None:
        runner = injected

    # Accept a plain dict (e.g. the diagnostics live-test path) as well as a Settings: resolve the
    # flag with .get + a local truthy check instead of Settings.get_bool (which a dict lacks).
    raw_connect = settings.get("adb_connect_before_switch", True)
    if isinstance(raw_connect, bool):
        do_connect = raw_connect
    else:
        do_connect = str(raw_connect).strip().lower() in ("1", "true", "yes", "on")
    if do_connect:
        adb_connect(adb_path, tv_ip, tv_port, runner=runner)

    return adb_shell(adb_path, tv_ip, tv_port, shell_command, runner=runner)
