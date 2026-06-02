"""A2 robustness: the TV switch tolerates odd command templates (L13) and a plain-dict
settings object on the ADB live-test path (M5)."""

import sys
import types
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _p in (str(ROOT), str(LIB)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from resources.lib.tv import tv_adb_control, tv_control


def test_run_external_tolerates_stray_braces_in_template():
    # L13: a template with an extra {placeholder} must not crash; {tv_ip} still substitutes.
    with mock.patch.object(tv_control.subprocess, "run") as run:
        run.return_value = types.SimpleNamespace(returncode=0, stdout="ok", stderr="")
        out = tv_control._run_external("echo {tv_ip} {tv_port}", {"tv_ip": "1.2.3.4"})
    assert out == "ok"
    argv = run.call_args[0][0]
    assert "1.2.3.4" in argv and "{tv_port}" in argv


def test_adb_switch_input_accepts_plain_dict_and_string_flag():
    # M5: a plain dict (no get_bool) must work; a string flag is parsed; a missing flag connects.
    calls = []

    def runner(args, **_):
        calls.append(args)
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    # string "false" -> no adb connect (covers the truthy-parse branch)
    tv_adb_control.switch_input(
        {"tv_ip": "1.2.3.4", "adb_connect_before_switch": "false"},
        "input keyevent 178",
        runner=runner,
    )
    assert all("connect" not in a for a in calls)
    # default (missing flag) -> adb connect runs first
    calls.clear()
    tv_adb_control.switch_input({"tv_ip": "1.2.3.4"}, "input keyevent 178", runner=runner)
    assert any("connect" in a for a in calls)
