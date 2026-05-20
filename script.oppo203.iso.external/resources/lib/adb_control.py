import shlex
import subprocess


class ADBError(RuntimeError):
    pass


def _run(args, timeout=15, runner=None):
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


def adb_connect(adb_path, host, port, runner=None):
    return _run([adb_path, "connect", f"{host}:{port}"], runner=runner)


def adb_shell(adb_path, host, port, command, runner=None):
    target = f"{host}:{port}"
    return _run([adb_path, "-s", target, "shell"] + shlex.split(command), runner=runner)


def switch_input(settings, shell_command, runner=None):
    adb_path = settings.get("adb_path", "adb")
    tv_ip = settings["tv_ip"]
    tv_port = int(settings.get("tv_adb_port", "5555"))
    injected = settings.get("_adb_runner", None)
    if injected is not None:
        runner = injected

    if settings.get_bool("adb_connect_before_switch", True):
        adb_connect(adb_path, tv_ip, tv_port, runner=runner)

    return adb_shell(adb_path, tv_ip, tv_port, shell_command, runner=runner)
