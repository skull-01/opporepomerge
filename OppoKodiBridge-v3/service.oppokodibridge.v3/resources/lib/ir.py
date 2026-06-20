"""Broadlink IR backend for CEC-free TV input switching.

This is the v3 endgame for HDMI switching: a network IR blaster (Broadlink RM4 mini) sends the TV's
own input-select IR codes, so the switch never touches the CEC bus (no Mi Box cross-control, no OPPO
power-cycle). It runs entirely over the LAN, so it works from the external player process with no
Kodi APIs.

``ir_code_oppo`` / ``ir_code_kodi`` each hold EITHER a single discrete IR code OR a comma-delimited
NAV SEQUENCE of learned codes (Source -> arrows -> OK), because the TCL Q9L Pro's bundled remote has
no discrete-HDMI button. A single discrete code is just a one-element sequence, so ``configured()``
and the settings format are unchanged. The low-level wire protocol lives in ``broadlink_rm4``; this
module is only the sequencing + reliability layer.
"""
from __future__ import annotations

import re
import time

from . import broadlink_rm4
from .kodilog import log

# The in-packet repeat byte is ONLY safe for a single discrete (idempotent) code; on a multi-key
# sequence it would emit every key twice (Source, Source, ...) and mis-land, so it is disabled for
# sequences (see ``_send``). Kept module constants until hardware tuning justifies a UI setting.
IR_REPEAT = 1
IR_KEY_GAP_MS = 200  # delay between keys of a multi-key nav sequence

_DELIM = re.compile(r"[,\n]")


def configured(config) -> bool:
    """True only when there is a Broadlink target and at least the switch-to-OPPO code."""
    return bool(getattr(config, "broadlink_ip", "") and getattr(config, "ir_code_oppo", ""))


def switch_to_oppo(config) -> bool:
    return _send(config, getattr(config, "ir_code_oppo", ""), "OPPO input")


def switch_to_kodi(config) -> bool:
    return _send(config, getattr(config, "ir_code_kodi", ""), "Kodi input")


def _tokens(code: str):
    return [t.strip() for t in _DELIM.split(code) if t.strip()]


def _send(config, code: str, label: str) -> bool:
    """Replay one discrete code or a nav sequence. Returns an honest bool: callers log on False and
    carry on (the OPPO still plays; a missed TV switch is correctable with the physical remote)."""
    if not code:
        log("IR: no code for {} -- skipping".format(label))
        return False
    ip = getattr(config, "broadlink_ip", "")
    if not ip:
        log("IR: no Broadlink IP -- skipping {}".format(label))
        return False

    tokens = _tokens(code)
    # Discrete code -> repeat is a safe, idempotent double-emit. Sequence -> repeat would double each
    # key and mis-land, so disable it.
    repeat = IR_REPEAT if len(tokens) == 1 else 0
    timeout = float(getattr(config, "socket_timeout", 4.0) or 4.0)

    try:
        dev = broadlink_rm4.RM4(ip, timeout=timeout).discover().auth()
    except OSError as exc:
        log("IR: RM4 {} unreachable ({}); leaving the TV as-is".format(ip, exc))
        return False

    gap = IR_KEY_GAP_MS / 1000.0
    for idx, token in enumerate(tokens):
        try:
            blob = broadlink_rm4.decode_ir_code(token)
        except ValueError as exc:
            log("IR: bad code for {} (token {}): {}".format(label, idx, exc))
            return False
        try:
            dev.send_ir(blob, repeat=repeat)
        except ValueError as exc:                     # not a 0x26 IR blob (e.g. an RF capture)
            log("IR: {} token {} is not an IR (0x26) code: {}".format(label, idx, exc))
            return False
        except OSError:                               # stale session / dropped packet: one re-auth+retry
            try:
                dev.discover().auth()
                dev.send_ir(blob, repeat=repeat)
            except (OSError, ValueError) as exc:
                log("IR: send failed mid-sequence for {} ({})".format(label, exc))
                return False
        if idx < len(tokens) - 1:
            time.sleep(gap)

    log("IR: switched the TV to {} ({} packet(s) sent)".format(label, len(tokens)))
    return True
