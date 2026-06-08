"""Kodi service: intercept local video playback and hand it to the OPPO.

When the user presses play in Kodi, ``onAVStarted`` fires with a valid file handle. We grab
the path, stop Kodi's local playback, and run the handoff on a background thread so the
service loop stays responsive. A re-entrancy guard keeps our own stop() from recursing.
"""
from __future__ import annotations

import threading

import xbmc

from . import cec
from . import config as config_mod
from .handoff import play_on_oppo
from .kodilog import log
from .oppo_http import is_oppo_target

_SKIP_PREFIXES = ("plugin://", "pvr://", "addons://", "script://")


class BridgePlayer(xbmc.Player):
    def __init__(self, service: "BridgeService") -> None:
        super().__init__()
        self._service = service

    def onAVStarted(self) -> None:
        self._service.on_local_play(self)


class BridgeService(xbmc.Monitor):
    def __init__(self) -> None:
        super().__init__()
        self._player = BridgePlayer(self)
        self._busy = threading.Event()
        self._lock = threading.Lock()
        log("OppoKodiBridge service started.")
        try:
            cfg = config_mod.from_addon()
            if cfg.cec_auto_enable:
                cec.ensure_kodi_cec_enabled()
        except Exception as exc:  # pragma: no cover - hardware path
            log("startup CEC check failed: {!r}".format(exc))
        cec.show_setup_guidance()

    def on_local_play(self, player: BridgePlayer) -> None:
        if self._busy.is_set():
            return
        try:
            if not player.isPlayingVideo():
                return
            path = player.getPlayingFile()
        except Exception:
            return
        if not path or path.startswith(_SKIP_PREFIXES):
            return
        try:
            cfg = config_mod.from_addon()
        except Exception as exc:  # pragma: no cover - hardware path
            log("could not read settings: {!r}".format(exc))
            return
        if not cfg.handoff_enabled or not cfg.configured:
            return
        # Filter: only disc images (.iso) and disc folders (BDMV/VIDEO_TS) go to the OPPO; let Kodi
        # play everything else (MKV, MP4, loose m2ts, ...) itself.
        if cfg.disc_iso_only and not is_oppo_target(path):
            log("Not a disc/ISO file; leaving playback in Kodi: {}".format(path))
            return
        with self._lock:
            if self._busy.is_set():
                return
            self._busy.set()
        log("Intercepting local playback: {}".format(path))
        try:
            player.stop()
        except Exception:
            pass
        threading.Thread(target=self._run_handoff, args=(cfg, path), daemon=True).start()

    def _run_handoff(self, cfg, path: str) -> None:
        try:
            play_on_oppo(cfg, path, should_abort=self.abortRequested)
        except Exception as exc:  # pragma: no cover - hardware path
            log("handoff thread error: {!r}".format(exc))
        finally:
            self._busy.clear()

    def run(self) -> None:
        while not self.abortRequested():
            if self.waitForAbort(1):
                break
        log("OppoKodiBridge service stopping.")


def main() -> None:
    BridgeService().run()
