"""Cross-language guard: the configurator's AutoScript generator + firmware gating must agree with
the add-on (the source of truth). The add-on side asserts ``autoscript_helper.generate()`` and
``settings_reader.oppo20x_autoscript_firmware_status`` reproduce the committed fixtures
(``configurator/src/autoscript/autoscript-fixtures.json``); the configurator side
(``autoscript.test.ts``) pins its TS mirror to the same fixtures. Mirrors the players/AVR-DB guard
pattern. If the add-on generator changes, regenerate the fixtures + update the TS mirror together.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (
    ROOT,
    os.path.join(ROOT, "resources", "lib"),
    os.path.join(ROOT, "resources", "lib", "oppo"),
    os.path.join(ROOT, "resources", "lib", "kodi"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)
for _n in ("xbmc", "xbmcaddon", "xbmcgui", "xbmcvfs"):
    sys.modules.pop(_n, None)

import autoscript_helper  # noqa: E402
import settings_reader  # noqa: E402

_FIXTURES = os.path.join(ROOT, "configurator", "src", "autoscript", "autoscript-fixtures.json")

# The same opt matrix configurator/src/autoscript/autoscript.test.ts pins, keyed identically.
CASES = {
    "default": {},
    "telnet_off": {"enable_telnet": False},
    "telnet_port_9999": {"telnet_port": 9999},
    "no_passwordless": {"passwordless_root": False},
    "nfs": {"mount_type": "nfs", "mount_remote": "10.0.1.10:/mnt/media"},
    "cifs_creds": {
        "mount_type": "cifs",
        "mount_remote": "//10.0.1.10/Media",
        "cifs_user": "kodi",
        "cifs_pass": "pw",
    },
    "adb_on": {"enable_adb": True, "adb_port": 5555},
    "no_heartbeat": {"heartbeat_path": ""},
    "full": {
        "enable_telnet": True,
        "telnet_port": 2323,
        "passwordless_root": True,
        "mount_type": "cifs",
        "mount_remote": "//nas/Media",
        "mount_local": "/tmp/share",
        "cifs_user": "u",
        "cifs_pass": "p",
        "enable_adb": True,
        "adb_port": 5555,
        "heartbeat_path": "/tmp/usb/sda1/oppo_autoexec_ran",
    },
}


def _fixtures():
    with open(_FIXTURES, encoding="utf-8") as f:
        return json.load(f)


def test_generator_matches_committed_fixtures():
    fx = _fixtures()
    assert set(fx) == set(CASES), "fixtures + CASES out of sync"
    for name, opts in CASES.items():
        assert autoscript_helper.generate(opts) == fx[name], name


def test_firmware_capability_thresholds_and_decisions():
    assert settings_reader.OPPO20X_AUTOSCRIPT_MIN_FIRMWARE == "20X-56"
    assert settings_reader.OPPO20X_AUTOSCRIPT_RECOMMENDED_FIRMWARE == "20X-65-0131"

    below = settings_reader.oppo20x_autoscript_firmware_status("20X-54-1127")
    assert below["autoscript_supported"] is False
    assert "oppo20x_firmware_below_20x_56" in below["blockers"]

    at_min = settings_reader.oppo20x_autoscript_firmware_status("20X-56")
    assert at_min["autoscript_supported"] is True
    assert "oppo20x_autoscript_supported_but_20x_65_0131_recommended" in at_min["warnings"]

    rec = settings_reader.oppo20x_autoscript_firmware_status("20X-65-0131")
    assert rec["autoscript_supported"] is True
    assert rec["warnings"] == []

    assert settings_reader.oppo20x_autoscript_firmware_status("")["autoscript_supported"] is None
