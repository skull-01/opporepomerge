"""The cec module: grab_oppo power-cycles the OPPO; reclaim_kodi posts the right localhost JSON-RPC to
trigger script.cecreclaim. Single-shot, never-reassert (the orchestrator calls each once)."""
import json

from resources.lib import cec
from resources.lib.config import Config


class _FakeClient:
    def __init__(self):
        self.cycled = 0

    def power_cycle(self):
        self.cycled += 1


def test_grab_oppo_power_cycles():
    client = _FakeClient()
    assert cec.grab_oppo(client) is True
    assert client.cycled == 1


def test_grab_oppo_nonfatal_on_error():
    class Boom:
        def power_cycle(self):
            raise cec.OppoError("nope")

    assert cec.grab_oppo(Boom()) is False


class _Resp:
    def __init__(self, body):
        self._b = body.encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_reclaim_kodi_posts_executeaddon(monkeypatch):
    cap = {}

    def fake_urlopen(req, timeout=None):
        cap["url"] = req.full_url
        cap["data"] = json.loads(req.data.decode())
        return _Resp(json.dumps({"jsonrpc": "2.0", "id": 1, "result": "OK"}))

    monkeypatch.setattr(cec.urllib.request, "urlopen", fake_urlopen)
    assert cec.reclaim_kodi(Config(oppo_ip="x", kodi_rpc_port=8080)) is True
    assert cap["url"] == "http://127.0.0.1:8080/jsonrpc"
    assert cap["data"]["method"] == "Addons.ExecuteAddon"
    assert cap["data"]["params"]["addonid"] == "script.cecreclaim"


def test_reclaim_kodi_false_on_unreachable(monkeypatch):
    def boom(req, timeout=None):
        raise OSError("no route to Kodi")

    monkeypatch.setattr(cec.urllib.request, "urlopen", boom)
    assert cec.reclaim_kodi(Config(oppo_ip="x")) is False


def test_reclaim_kodi_false_on_rpc_error(monkeypatch):
    monkeypatch.setattr(
        cec.urllib.request, "urlopen",
        lambda req, timeout=None: _Resp(json.dumps({"jsonrpc": "2.0", "id": 1, "error": {"message": "no"}})),
    )
    assert cec.reclaim_kodi(Config(oppo_ip="x")) is False
