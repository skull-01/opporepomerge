"""app.on_save must surface a write failure in the log: the app is packaged --noconsole, so an
unhandled exception would vanish and silently lose the user's settings."""
import os
import sys

import pytest

pytest.importorskip("tkinter")  # app.py imports tkinter at module load
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app as appmod  # noqa: E402


class _Stub:
    """Minimal stand-in bound to App.on_save -- avoids building the full Tk UI."""

    def __init__(self):
        self.logged = []
        self.cfg = None

    def _current(self):
        return {"oppo_ip": "x"}

    def _log(self, msg):
        self.logged.append(msg)


def test_on_save_surfaces_write_failure(monkeypatch):
    def boom(cfg):
        raise OSError("read-only config dir")

    monkeypatch.setattr(appmod, "save_config", boom)
    stub = _Stub()
    appmod.App.on_save(stub)  # must not raise
    assert any("FAILED" in m for m in stub.logged)


def test_on_save_logs_saved_on_success(monkeypatch):
    saved = []
    monkeypatch.setattr(appmod, "save_config", lambda cfg: saved.append(cfg))
    stub = _Stub()
    appmod.App.on_save(stub)
    assert saved and any("Saved" in m for m in stub.logged)
