"""CEC Switcher -- a 2-button LAN remote that tells the OPPO or the Kodi box to take CEC ownership.

The PC is NOT on the HDMI/CEC bus. This app triggers each device's OWN CEC One-Touch-Play over the
network (legitimate -- no spoofing): the OPPO via a TCP power-cycle, Kodi via the script.cecreclaim
helper. Run from source (``python app.py``) or as the packaged ``CEC-Switcher.exe`` (see build.ps1).
"""
from __future__ import annotations

import json
import os
import threading
import tkinter as tk
from tkinter import ttk

import cec_core

CONFIG_DIR = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "CECSwitcher")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
DEFAULTS = {
    "oppo_ip": "192.168.10.10",
    "kodi_ip": "192.168.1.100",
    "kodi_port": 8080,
    "kodi_user": "",
    "kodi_pass": "",
}


def load_config() -> dict:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
            return {**DEFAULTS, **json.load(fh)}
    except Exception:
        return dict(DEFAULTS)


def save_config(cfg: dict) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)


class App:
    def __init__(self, root: "tk.Tk"):
        self.root = root
        self.cfg = load_config()
        root.title("CEC Switcher")
        root.minsize(400, 380)

        frm = ttk.Frame(root, padding=12)
        frm.pack(fill="both", expand=True)
        pad = {"padx": 6, "pady": 4}

        ttk.Label(frm, text="OPPO IP").grid(row=0, column=0, sticky="w", **pad)
        self.oppo_ip = tk.StringVar(value=self.cfg["oppo_ip"])
        ttk.Entry(frm, textvariable=self.oppo_ip, width=24).grid(row=0, column=1, sticky="ew", **pad)

        ttk.Label(frm, text="Kodi IP").grid(row=1, column=0, sticky="w", **pad)
        self.kodi_ip = tk.StringVar(value=self.cfg["kodi_ip"])
        ttk.Entry(frm, textvariable=self.kodi_ip, width=24).grid(row=1, column=1, sticky="ew", **pad)

        ttk.Label(frm, text="Kodi port").grid(row=2, column=0, sticky="w", **pad)
        self.kodi_port = tk.StringVar(value=str(self.cfg["kodi_port"]))
        ttk.Entry(frm, textvariable=self.kodi_port, width=8).grid(row=2, column=1, sticky="w", **pad)

        row = ttk.Frame(frm)
        row.grid(row=3, column=0, columnspan=2, pady=(2, 6))
        ttk.Button(row, text="Save", command=self.on_save).pack(side="left", padx=4)
        ttk.Button(row, text="Test (ping both)", command=self.on_test).pack(side="left", padx=4)

        ttk.Separator(frm, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=6)

        self.btn_oppo = ttk.Button(frm, text="▶  Switch to OPPO", command=self.on_oppo)
        self.btn_oppo.grid(row=5, column=0, columnspan=2, sticky="ew", pady=4, ipady=10)
        self.btn_kodi = ttk.Button(frm, text="\U0001f3e0  Switch to Kodi", command=self.on_kodi)
        self.btn_kodi.grid(row=6, column=0, columnspan=2, sticky="ew", pady=4, ipady=10)

        self.log = tk.Text(frm, height=8, width=46, state="disabled", wrap="word")
        self.log.grid(row=7, column=0, columnspan=2, sticky="nsew", pady=(8, 0))

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(7, weight=1)
        self._log("Ready. The PC isn't on the CEC bus -- it tells each box to grab the TV itself.")

    # --- helpers ---
    def _log(self, msg: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _async(self, fn) -> None:
        def worker():
            try:
                msg = fn()
            except Exception as exc:  # noqa: BLE001 - surface any failure in the log, never crash
                msg = "ERROR: {}".format(exc)
            self.root.after(0, lambda: self._log(str(msg)))

        threading.Thread(target=worker, daemon=True).start()

    def _current(self) -> dict:
        try:
            port = int(self.kodi_port.get() or 8080)
        except ValueError:
            port = 8080
        return {
            "oppo_ip": self.oppo_ip.get().strip(),
            "kodi_ip": self.kodi_ip.get().strip(),
            "kodi_port": port,
            "kodi_user": self.cfg.get("kodi_user", ""),
            "kodi_pass": self.cfg.get("kodi_pass", ""),
        }

    # --- actions ---
    def on_save(self) -> None:
        self.cfg = self._current()
        try:
            save_config(self.cfg)
        except OSError as exc:
            # The only persistence path -- surface a write failure in the log (the app is packaged
            # --noconsole, so an unhandled exception would vanish and silently lose the settings).
            self._log("Save FAILED: {}".format(exc))
            return
        self._log("Saved settings.")

    def on_test(self) -> None:
        cfg = self._current()
        self._log("Pinging OPPO {} ...".format(cfg["oppo_ip"]))
        self._async(lambda: "OPPO: reachable" if cec_core.ping_oppo(cfg["oppo_ip"]) else "OPPO: UNREACHABLE")
        self._log("Pinging Kodi {}:{} ...".format(cfg["kodi_ip"], cfg["kodi_port"]))
        self._async(lambda: "Kodi: reachable ({})".format(
            cec_core.kodi_ping(cfg["kodi_ip"], port=cfg["kodi_port"],
                               user=cfg["kodi_user"], password=cfg["kodi_pass"])))

    def on_oppo(self) -> None:
        cfg = self._current()
        self._log("Switch to OPPO: power-cycling {} (TV follows in ~20-24s) ...".format(cfg["oppo_ip"]))
        self._async(lambda: cec_core.oppo_take_tv(cfg["oppo_ip"]))

    def on_kodi(self) -> None:
        cfg = self._current()
        self._log("Switch to Kodi: triggering CECActivateSource on {} ...".format(cfg["kodi_ip"]))

        def go():
            cec_core.kodi_take_tv(cfg["kodi_ip"], port=cfg["kodi_port"],
                                  user=cfg["kodi_user"], password=cfg["kodi_pass"])
            return "Kodi reclaim sent (script.cecreclaim -> CECActivateSource)."

        self._async(go)


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
