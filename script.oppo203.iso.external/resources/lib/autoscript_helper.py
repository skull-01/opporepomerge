"""Chinoppo AutoScript generator (v1.0.3)."""

import os

try:
    import xbmc
    import xbmcaddon
    import xbmcgui
    import xbmcvfs
except ImportError:
    xbmc = xbmcaddon = xbmcgui = xbmcvfs = None
ADDON_ID = "script.oppo203.iso.external"


def _profile(addon):
    if addon is None or xbmcvfs is None:
        return os.path.join(os.path.expanduser("~"), ".kodi-" + ADDON_ID)
    return xbmcvfs.translatePath(addon.getAddonInfo("profile"))


def _safe_int(v, default):
    try:
        return int(v)
    except (TypeError, ValueError):
        return int(default)


def generate(opts):
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


def write_script(path, body):
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    with open(path, "w", newline="\n") as f:
        f.write(body)
    try:
        os.chmod(path, 0o755)
    except Exception:
        pass
    return path


def _yn(t, m):
    return bool(xbmcgui.Dialog().yesno(t, m)) if xbmcgui else False


def _ok(t, m):
    if xbmcgui:
        xbmcgui.Dialog().ok(t, m)


def _in(t, d=""):
    if xbmcgui:
        v = xbmcgui.Dialog().input(t, d)
        return v if v else d
    return d


def _sel(t, opts):
    if xbmcgui:
        i = xbmcgui.Dialog().select(t, opts)
        return i if i >= 0 else 0
    return 0


def run_autoscript_wizard(addon=None):
    if addon is None:
        addon = xbmcaddon.Addon(ADDON_ID) if xbmcaddon else None
    _ok("Chinoppo AutoScript", "Generate autoexec.sh.")
    et = _yn("Telnet", "Enable telnetd 2323?")
    pr = _yn("Passwordless root", "Enable passwordless root?")
    mt_idx = _sel("Mount", ["No mount", "NFS", "CIFS"])
    mt = ["none", "nfs", "cifs"][mt_idx]
    mr = cu = cp = ""
    if mt == "nfs":
        mr = _in("NFS host:/path", "192.168.1.10:/srv/movies")
    elif mt == "cifs":
        mr = _in("CIFS //host/share", "//192.168.1.10/movies")
        cu = _in("Username", "")
        if cu:
            cp = _in("Password", "")
    hb = _in("Heartbeat", "/tmp/usb/sda1/oppo_autoexec_ran")
    ea = _yn("ADB", "Enable ADB on TCP 5555?")
    body = generate(
        {
            "enable_telnet": et,
            "passwordless_root": pr,
            "mount_type": mt,
            "mount_remote": mr,
            "cifs_user": cu,
            "cifs_pass": cp,
            "heartbeat_path": hb,
            "enable_adb": ea,
        }
    )
    out_dir = _profile(addon)
    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception:
        pass
    out = os.path.join(out_dir, "autoexec.sh")
    write_script(out, body)
    _ok("AutoScript generated", "Wrote: " + out)
    return out
