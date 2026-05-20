import sys

from resources.lib.installer import main
from resources.lib.oppo_remote import send_remote_key

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "oppo_key":
        send_remote_key(sys.argv[2])
    else:
        main()


def run_diagnostics_dashboard(addon_data_dir=None, host=None, port=23, mac=None):
    """Installer menu entry point for the v1.0.9 diagnostics dashboard.

    Wires real Kodi-aware probes via best-effort lazy imports; falls
    back to skipped probes when Kodi APIs are unavailable.  Returns the
    written report path or None if `addon_data_dir` is None.
    """
    try:
        from resources.lib import diagnostics as diag
    except ImportError:
        try:
            from .resources.lib import diagnostics as diag
        except Exception:
            import importlib, sys, os as _os
            sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), "resources", "lib"))
            diag = importlib.import_module("diagnostics")

    def _tcp(h, p):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        try:
            s.connect((h, int(p))); s.close()
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _http(h):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        try:
            s.connect((h, 80)); s.close()
            return {"ok": True, "port": 80}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _svm(h, p):
        # Capability probe only: we attempt to send "#SVM 2\r" and read
        # one line; success is any non-empty reply.
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        try:
            s.connect((h, int(p)))
            s.sendall(b"#SVM 2\r")
            data = s.recv(64)
            s.close()
            return {"ok": bool(data), "reply_bytes": len(data or b"")}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _wol(m):
        # Best-effort: send a magic packet; "round-trip" here means the
        # packet was sent without OS error.  Real ARP/return is out of
        # scope for a Kodi sandbox.
        import socket
        try:
            mac = m.replace(":","").replace("-","")
            if len(mac) != 12: return {"ok": False, "error": "bad MAC"}
            payload = bytes.fromhex("FF"*6 + mac*16)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(payload, ("255.255.255.255", 9))
            sock.close()
            return {"ok": True, "bytes": len(payload)}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _kodi():
        try:
            import xbmc
            return {"ok": True,
                    "build_version": xbmc.getInfoLabel("System.BuildVersion"),
                    "kernel": xbmc.getInfoLabel("System.KernelVersion")}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _caps():
        return {"ok": True,
                "service_interception": True,
                "external_player": True,
                "wol": True,
                "verbose_push": True}

    res = diag.run(host, port, mac,
                   tcp_check=_tcp, http_check=_http, svm_check=_svm,
                   wol_check=_wol, kodi_info=_kodi, capabilities=_caps)
    if addon_data_dir:
        return diag.save_report(res, addon_data_dir)
    return None
