"""Broadlink IR backend for CEC-free TV input switching.

This is the v3 endgame for HDMI switching: a network IR blaster (Broadlink RM4 mini) sends the TV's
own input-select IR codes, so the switch is instant and never touches the CEC bus (no Mi Box
cross-control, no power-cycle). It runs entirely over the LAN, so it works from the external player
process with no Kodi APIs.

STATUS: stubbed until the RM4 is in hand. ``configured()`` is False unless a Broadlink IP and the
"switch to OPPO" IR code are both set, so the handoff falls back to the interim OPPO power-cycle.
When the device arrives, ``_send`` gets the real discover/auth/send implementation (vendor a
pure-Python Broadlink client + AES).
"""
from __future__ import annotations

from .kodilog import log


def configured(config) -> bool:
    """True only when there is a Broadlink target and at least the switch-to-OPPO code."""
    return bool(getattr(config, "broadlink_ip", "") and getattr(config, "ir_code_oppo", ""))


def switch_to_oppo(config) -> bool:
    return _send(config, getattr(config, "ir_code_oppo", ""), "OPPO input")


def switch_to_kodi(config) -> bool:
    return _send(config, getattr(config, "ir_code_kodi", ""), "Kodi input")


def _send(config, code: str, label: str) -> bool:
    if not code:
        log("IR: no code for {} -- skipping".format(label))
        return False
    ip = getattr(config, "broadlink_ip", "")
    # TODO(RM4): real Broadlink send -- discover/auth by IP, then send the base64/hex IR packet.
    log("IR: would switch TV to {} via Broadlink {} (not yet implemented)".format(label, ip))
    return False
