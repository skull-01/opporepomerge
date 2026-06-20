"""Generate and install the ``playercorefactory.xml`` that routes disc content to the OPPO.

This is the heart of v3: instead of a service monitor stopping playback after it starts (the v2
"Kodi blips then hands off" behaviour), Kodi's playercorefactory routes ``.iso`` and BDMV/VIDEO_TS
content to an *external player* before Kodi's own player ever touches the file -- so there is no blip.

The external player is ``pcf_player.py`` at the add-on root, invoked as ``python3 pcf_player.py {1}``
where Kodi substitutes ``{1}`` with the file it would have played.
"""
from __future__ import annotations

import os

from .kodilog import log

PLAYER_NAME = "OppoKodiBridge"

# {1} is Kodi's substitution token and must survive verbatim, so the template uses __PLACEHOLDERS__
# and str.replace rather than str.format (which would choke on the braces and the regex backslashes).
_TEMPLATE = """<playercorefactory>
  <players>
    <player name="__NAME__" type="ExternalPlayer" audio="false" video="true">
      <filename>__PY__</filename>
      <args>"__SCRIPT__" "{1}"</args>
      <hidexbmc>true</hidexbmc>
      <hideconsole>true</hideconsole>
      <warnoffscreen>false</warnoffscreen>
      <islauncher>false</islauncher>
    </player>
  </players>
  <rules action="prepend">
    <rule filetypes="iso" player="__NAME__"/>
    <rule filename="(?i).*/bdmv/.*" player="__NAME__"/>
    <rule filename="(?i).*/video_ts/.*" player="__NAME__"/>
    <rule filename="(?i).*\\.bdmv$" player="__NAME__"/>
    <rule filename="(?i).*\\.iso$" player="__NAME__"/>
  </rules>
</playercorefactory>
"""


def build_xml(player_script_path: str, python_bin: str = "python3") -> str:
    """The playercorefactory.xml content routing disc content to ``player_script_path``."""
    return (
        _TEMPLATE.replace("__NAME__", PLAYER_NAME)
        .replace("__PY__", python_bin)
        .replace("__SCRIPT__", player_script_path)
    )


def install(profile_dir: str, player_script_path: str, python_bin: str = "python3") -> bool:
    """Write ``playercorefactory.xml`` into the Kodi profile dir. Backs up an existing file once."""
    target = os.path.join(profile_dir, "playercorefactory.xml")
    content = build_xml(player_script_path, python_bin)
    try:
        if os.path.exists(target):
            backup = target + ".okbv3-backup"
            if not os.path.exists(backup):
                with open(target, "r", encoding="utf-8", errors="replace") as src:
                    existing = src.read()
                if PLAYER_NAME not in existing:  # don't back up our own previous write
                    with open(backup, "w", encoding="utf-8") as dst:
                        dst.write(existing)
                    log("backed up existing playercorefactory.xml -> {}".format(backup))
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(content)
        log("playercorefactory.xml installed -> {}".format(target))
        return True
    except OSError as exc:  # pragma: no cover - hardware path
        log("failed to install playercorefactory.xml: {}".format(exc))
        return False


def uninstall(profile_dir: str) -> bool:
    """Remove our playercorefactory.xml (restoring a backup if we made one)."""
    target = os.path.join(profile_dir, "playercorefactory.xml")
    backup = target + ".okbv3-backup"
    try:
        if os.path.exists(backup):
            with open(backup, "r", encoding="utf-8", errors="replace") as src:
                restored = src.read()
            with open(target, "w", encoding="utf-8") as fh:
                fh.write(restored)
            os.remove(backup)
            log("restored playercorefactory.xml from backup")
        elif os.path.exists(target):
            os.remove(target)
            log("removed playercorefactory.xml")
        return True
    except OSError as exc:  # pragma: no cover - hardware path
        log("failed to uninstall playercorefactory.xml: {}".format(exc))
        return False
