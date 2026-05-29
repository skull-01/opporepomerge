"""Guards for the fast local test loop wrapper (tools/dev_test.py).

The wrapper is a developer convenience that runs only the tests affected by a
change via pytest-testmon. These checks lock in the two gotchas that make it
work and confirm it never ships in the runtime ZIP.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_command_activates_testmon_and_keeps_cacheprovider() -> None:
    from tools import dev_test

    cmd = dev_test.build_command("py", ["-k", "yamaha"], on_windows=False)
    assert cmd[:4] == ["py", "-m", "pytest", "--testmon"]
    assert cmd[-2:] == ["-k", "yamaha"]
    # testmon reads the cacheprovider 'lf' option; disabling it raises KeyError.
    assert "no:cacheprovider" not in " ".join(cmd)


def test_command_pins_basetemp_only_on_windows() -> None:
    from tools import dev_test

    win = dev_test.build_command("py", [], on_windows=True)
    posix = dev_test.build_command("py", [], on_windows=False)
    assert win[-2:] == ["--basetemp", dev_test.WINDOWS_BASETEMP]
    assert "--basetemp" not in posix


def test_env_routes_temp_outside_repo_on_windows_only() -> None:
    from tools import dev_test

    scratch = Path("X:/scratch")
    win = dev_test.testmon_env({}, on_windows=True, scratch_dir=scratch)
    posix = dev_test.testmon_env({}, on_windows=False, scratch_dir=scratch)
    assert win["TEMP"] == str(scratch)
    assert win["TMP"] == str(scratch)
    assert "TEMP" not in posix and "TMP" not in posix


def test_dev_test_is_not_a_runtime_member() -> None:
    from tools import package_installable_zip as package_tool

    assert package_tool.is_runtime_member("tools/dev_test.py") is False


def test_testmon_is_a_dev_dependency() -> None:
    text = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
    assert "pytest-testmon" in text
