import json
import sys

import pytest

from resources.lib import cec


class FakeXbmc:
    LOGINFO = 1
    LOGERROR = 4

    def __init__(self):
        self.builtins = []
        self.jsonrpc_handler = None

    def log(self, message, level=1):
        pass

    def executebuiltin(self, command):
        self.builtins.append(command)

    def executeJSONRPC(self, request):
        return self.jsonrpc_handler(request)


@pytest.fixture
def fake_xbmc(monkeypatch):
    fx = FakeXbmc()
    monkeypatch.setitem(sys.modules, "xbmc", fx)
    return fx


def test_reclaim_tv_calls_builtin(fake_xbmc):
    assert cec.reclaim_tv() is True
    assert "CECActivateSource" in fake_xbmc.builtins


def test_aocec_active_source_frame():
    assert cec._aocec_active_source_frame("1.0.0.0") == "4f 82 10 00"
    assert cec._aocec_active_source_frame("2.0.0.0") == "4f 82 20 00"
    assert cec._aocec_active_source_frame("1.1.0.0") == "4f 82 11 00"


def test_ensure_enables_when_off(fake_xbmc):
    applied = []

    def handler(request):
        req = json.loads(request)
        if req["method"] == "Settings.GetSettingValue":
            return json.dumps({"id": 1, "result": {"value": False}})
        if req["method"] == "Settings.SetSettingValue":
            applied.append(req["params"])
            return json.dumps({"id": 1, "result": True})
        return json.dumps({})

    fake_xbmc.jsonrpc_handler = handler
    assert cec.ensure_kodi_cec_enabled() is True
    assert applied and applied[0]["value"] is True


def test_ensure_noop_when_on(fake_xbmc):
    applied = []

    def handler(request):
        req = json.loads(request)
        if req["method"] == "Settings.GetSettingValue":
            return json.dumps({"id": 1, "result": {"value": True}})
        applied.append(req)
        return json.dumps({"id": 1, "result": True})

    fake_xbmc.jsonrpc_handler = handler
    assert cec.ensure_kodi_cec_enabled() is True
    assert applied == []


def test_ensure_handles_missing_setting(fake_xbmc):
    def handler(request):
        return json.dumps({"id": 1, "error": {"code": -32602, "message": "Invalid params"}})

    fake_xbmc.jsonrpc_handler = handler
    assert cec.ensure_kodi_cec_enabled() is False
