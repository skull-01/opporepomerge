#!/usr/bin/env python3
"""External player invoked by Kodi's playercorefactory: ``python3 pcf_player.py "<file>"``.

Runs OUTSIDE Kodi (its own process, no xbmc). Reads the config the service published to
``runtime_config.json``, then hands the file to the OPPO over the network and blocks until playback
ends. Because Kodi routed the file here *before* playing it, there is no "Kodi blips then hands off"
moment -- that's the whole point of this no-blip fork.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from resources.lib import cec_reclaim  # noqa: E402
from resources.lib import config as config_mod  # noqa: E402
from resources.lib import handoff  # noqa: E402
from resources.lib.kodilog import log  # noqa: E402

ADDON_ID = "service.oppokodibridge.cec"


def _runtime_config_path() -> str:
    # HERE = <kodi>/addons/<id> ; the service writes config to <kodi>/userdata/addon_data/<id>/.
    kodi_home = os.path.dirname(os.path.dirname(HERE))
    return os.path.join(kodi_home, "userdata", "addon_data", ADDON_ID, "runtime_config.json")


def _data_dir() -> str:
    return os.path.dirname(_runtime_config_path())


def _load_config():
    path = _runtime_config_path()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return config_mod.Config.from_dict(json.load(fh))
    except Exception as exc:
        log("pcf_player: could not load {} ({!r}); using defaults".format(path, exc))
        return config_mod.Config()


def main(argv) -> int:
    if len(argv) < 2 or not argv[1]:
        log("pcf_player: no file argument given")
        return 2
    kodi_file = argv[1]
    log("pcf_player: handling {!r}".format(kodi_file))
    cfg = _load_config()
    rc = 0
    try:
        handoff.play_on_oppo(cfg, kodi_file)
    except Exception as exc:  # never crash the player process
        log("pcf_player: handoff error {!r}".format(exc))
        rc = 1
    finally:
        # Single-shot Kodi reclaim: now that the handoff has ended, signal the in-Kodi service ONCE to
        # re-assert Kodi's own active source (CECActivateSource). Never a standing re-asserter -- a
        # manual input change must stick (see resources/lib/cec_reclaim.py).
        if getattr(cfg, "cec_reclaim_on_stop", True):
            if cec_reclaim.request(_data_dir()):
                log("pcf_player: requested a one-shot Kodi CEC reclaim")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
