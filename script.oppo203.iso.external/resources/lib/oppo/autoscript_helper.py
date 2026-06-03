"""Chinoppo AutoScript generator (v1.0.3)."""

from __future__ import annotations

import os
from typing import Any


def _safe_int(v: Any, default: int) -> int:
    try:
        return int(v)
    except (TypeError, ValueError, OverflowError):
        # OverflowError covers int(float("inf")); a JSON-loaded preset can carry a
        # non-finite float for telnet_port/adb_port. Matches the repo-wide guard
        # pattern (oppo_control, i18n) so the generator degrades to the default.
        return int(default)


def generate(opts: dict[str, Any] | None) -> str:
    o = dict(opts or {})
    et = bool(o.get("enable_telnet", True))
    tp = _safe_int(o.get("telnet_port", 2323), 2323)
    pr = bool(o.get("passwordless_root", True))
    mt = str(o.get("mount_type", "none") or "none").lower()
    mr = o.get("mount_remote", "")
    ml = o.get("mount_local", "/tmp/share")
    mo = o.get("mount_options", "")
    cu = o.get("cifs_user", "")
    cp = o.get("cifs_pass", "")
    hb = o.get("heartbeat_path", "/tmp/usb/sda1/oppo_autoexec_ran")
    ea = bool(o.get("enable_adb", False))
    ap = _safe_int(o.get("adb_port", 5555), 5555)
    L = [
        "#!/bin/sh",
        "# autoexec.sh - Chinoppo AutoScript v1.0.3",
        "set +e",
        "LOG=/tmp/oppo_autoexec.log",
        'echo "[autoexec] starting" > "$LOG"',
        "",
    ]
    if hb:
        L += ['echo "started" > "' + hb + '" 2>>"$LOG" || true', ""]
    if pr:
        L += [
            "sed -i 's|^root:[^:]*|root:|' /etc/shadow 2>>\"$LOG\" || true",
            "sed -i 's|^root:[^:]*|root:|' /etc/passwd 2>>\"$LOG\" || true",
            "",
        ]
    if et:
        L += [
            "if ! pidof telnetd >/dev/null 2>&1; then",
            "  telnetd -p " + str(tp) + ' -l /bin/sh >>"$LOG" 2>&1 &',
            "fi",
            "",
        ]
    if mt in ("nfs", "cifs") and mr:
        L += ['mkdir -p "' + ml + '"']
        if mt == "nfs":
            opt = mo or "nolock,soft,intr,vers=3"
            L.append("mount -t nfs -o " + opt + ' "' + mr + '" "' + ml + '" >>"$LOG" 2>&1 || true')
        else:
            opt = mo or "iocharset=utf8,vers=2.0"
            cred = ""
            if cu:
                cred = ",username=" + cu
                if cp:
                    cred += ",password=" + cp
            L.append(
                "mount -t cifs -o "
                + opt
                + cred
                + ' "'
                + mr
                + '" "'
                + ml
                + '" >>"$LOG" 2>&1 || true'
            )
        L.append("")
    if ea:
        L += [
            "setprop service.adb.tcp.port " + str(ap) + ' 2>>"$LOG" || true',
            'stop adbd 2>>"$LOG" || true',
            'start adbd 2>>"$LOG" || true',
            "",
        ]
    if hb:
        L += ['echo "completed" >> "' + hb + '" 2>>"$LOG" || true', ""]
    L += ['echo "[autoexec] done" >> "$LOG"', "exit 0", ""]
    return "\n".join(L)


def write_script(path: str, body: str) -> str:
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    with open(path, "w", newline="\n") as f:
        f.write(body)
    try:
        os.chmod(path, 0o755)
    except Exception:
        pass
    return path
