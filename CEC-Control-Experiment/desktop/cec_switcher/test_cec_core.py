"""Off-box tests for the CEC Switcher network logic (no hardware). The OPPO side is exercised against
a fake TCP server; the Kodi side monkeypatches urlopen. The GUI (app.py) is not tested here."""
import json
import os
import socket
import struct
import sys
import threading
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cec_core  # noqa: E402


# --- fake OPPO control port (#XXX over TCP) ---
class FakeOppo:
    def __init__(self, reply_map=None):
        self.reply_map = reply_map or {}
        self.received = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(5)
        self.port = self.sock.getsockname()[1]
        self._stop = False
        self._t = threading.Thread(target=self._serve, daemon=True)
        self._t.start()

    def _serve(self):
        self.sock.settimeout(0.3)
        while not self._stop:
            try:
                conn, _ = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            with conn:
                conn.settimeout(0.5)
                try:
                    data = conn.recv(64)
                except socket.timeout:
                    data = b""
                cmd = data.decode("ascii", "replace").strip()
                self.received.append(cmd)
                reply = self.reply_map.get(cmd)
                if reply:
                    try:
                        conn.sendall((reply + "\r").encode())
                    except OSError:
                        pass

    def close(self):
        self._stop = True
        self.sock.close()


def _wait(pred, timeout=2.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if pred():
            return True
        time.sleep(0.02)
    return False


def test_oppo_take_tv_power_cycles():
    srv = FakeOppo()
    slept = []
    try:
        msg = cec_core.oppo_take_tv("127.0.0.1", port=srv.port, gap=3.0, sleep=lambda s: slept.append(s))
        assert _wait(lambda: "#POF" in srv.received and "#PON" in srv.received), srv.received
        assert srv.received.index("#POF") < srv.received.index("#PON")
        assert slept == [3.0]                      # waited between off and on (sleep injected)
        assert "power-cycle" in msg.lower()
    finally:
        srv.close()


def test_oppo_query_power_parses_on():
    srv = FakeOppo(reply_map={"#QPW": "@QPW OK ON"})
    try:
        assert cec_core.oppo_query_power("127.0.0.1", port=srv.port) == "ON"
    finally:
        srv.close()


def test_ping_oppo_true_and_false():
    srv = FakeOppo(reply_map={"#QPW": "@QPW OK OFF"})
    try:
        assert cec_core.ping_oppo("127.0.0.1", port=srv.port) is True
    finally:
        srv.close()
    # nothing listening on this port -> unreachable
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    dead = s.getsockname()[1]
    s.close()
    assert cec_core.ping_oppo("127.0.0.1", port=dead, timeout=0.3) is False


# --- Kodi JSON-RPC (monkeypatched urlopen) ---
class _FakeResp:
    def __init__(self, body):
        self._b = body.encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_kodi_take_tv_posts_executeaddon(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["data"] = json.loads(req.data.decode())
        return _FakeResp(json.dumps({"jsonrpc": "2.0", "id": 1, "result": "OK"}))

    monkeypatch.setattr(cec_core.urllib.request, "urlopen", fake_urlopen)
    assert cec_core.kodi_take_tv("192.168.1.100", port=8080) == "OK"
    assert captured["url"] == "http://192.168.1.100:8080/jsonrpc"
    assert captured["data"]["method"] == "Addons.ExecuteAddon"
    assert captured["data"]["params"]["addonid"] == "script.cecreclaim"


def test_kodi_ping_returns_pong(monkeypatch):
    monkeypatch.setattr(
        cec_core.urllib.request, "urlopen",
        lambda req, timeout=None: _FakeResp(json.dumps({"jsonrpc": "2.0", "id": 1, "result": "pong"})),
    )
    assert cec_core.kodi_ping("x") == "pong"


def test_kodi_error_raises(monkeypatch):
    monkeypatch.setattr(
        cec_core.urllib.request, "urlopen",
        lambda req, timeout=None: _FakeResp(
            json.dumps({"jsonrpc": "2.0", "id": 1, "error": {"code": -1, "message": "nope"}})),
    )
    with pytest.raises(OSError):
        cec_core.kodi_take_tv("x")


def test_oppo_take_tv_sends_pon_when_poff_fails(monkeypatch):
    # b6 parity: a failed #POF must not skip #PON (the leg that fires the One-Touch-Play).
    sent = []

    def fake_send(ip, command, port=cec_core.OPPO_TCP_PORT, timeout=4.0, read=True):
        if command == "#POF":
            raise ConnectionResetError("reset")
        sent.append(command)
        return ""

    monkeypatch.setattr(cec_core, "_oppo_send", fake_send)
    msg = cec_core.oppo_take_tv("127.0.0.1", gap=0, sleep=lambda s: None)
    assert sent == ["#PON"]
    assert "power-cycle" in msg.lower()


def test_ping_oppo_true_when_peer_resets_before_reply():
    # b11: a peer that accepts then RSTs before replying is still reachable -> ping True (was False).
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port = srv.getsockname()[1]

    def serve():
        conn, _ = srv.accept()
        try:
            conn.recv(64)  # read the #QPW so the client's send succeeds
        except OSError:
            pass
        conn.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
        conn.close()  # force an RST

    t = threading.Thread(target=serve, daemon=True)
    t.start()
    try:
        assert cec_core.ping_oppo("127.0.0.1", port=port, timeout=1.0) is True
    finally:
        srv.close()


def test_oppo_take_tv_m9207_sends_ejt(monkeypatch):
    # model selection parity: the desktop switcher grabs an M9207 with a single #EJT, no #POF/#PON.
    sent = []

    def fake_send(ip, command, port=cec_core.OPPO_TCP_PORT, timeout=4.0, read=True):
        sent.append(command)
        return ""

    monkeypatch.setattr(cec_core, "_oppo_send", fake_send)
    msg = cec_core.oppo_take_tv("127.0.0.1", gap=0, sleep=lambda s: None, model="M9207")
    assert sent == ["#EJT"]
    assert "eject" in msg.lower()
