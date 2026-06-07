import json
import urllib.parse

from resources.lib import oppo_http as oh
from resources.lib.config import Config


def test_parse_network_share_nfs():
    assert oh.parse_network_share("nfs://192.168.10.20/srv/nfs/media/Gina.mp4") == (
        "nfs",
        "192.168.10.20",
        "srv",
    )


def test_parse_network_share_smb():
    assert oh.parse_network_share("smb://nas/Movies/x.mkv") == ("smb", "nas", "Movies")


def test_parse_network_share_local_is_none():
    assert oh.parse_network_share("/mnt/nas/media/x.mkv") is None


def test_apply_path_rewrite_matches_prefix():
    out = oh.apply_path_rewrite(
        "nfs://192.168.10.20/srv/nfs/media/Gina.mp4",
        "nfs://192.168.10.20/srv/nfs/media",
        "/mnt/nas/media",
    )
    assert out == "/mnt/nas/media/Gina.mp4"


def test_apply_path_rewrite_no_match_passthrough():
    assert oh.apply_path_rewrite("/local/x", "nfs://a/b", "/mnt") == "/local/x"


def test_build_play_payload_shape():
    assert oh.build_play_payload("/mnt/nas/media/Gina.mp4", 1, 2) == {
        "path": "/mnt/nas/media/Gina.mp4",
        "index": 0,
        "type": 1,
        "appDeviceType": 2,
        "extraNetPath": "",
        "playMode": 0,
    }


def test_status_is_idle():
    assert oh.status_is_idle("STOP")
    assert oh.status_is_idle("")
    assert not oh.status_is_idle("PLAY")
    assert not oh.status_is_idle("loading")


def test_info_is_playing():
    assert oh.info_is_playing({"is_playing": True})
    assert oh.info_is_playing({"result": {"status": "PLAY"}})
    assert not oh.info_is_playing({"result": {"status": "STOP"}})
    assert not oh.info_is_playing({})


def test_play_builds_json_payload(monkeypatch):
    cfg = Config(
        oppo_ip="1.2.3.4",
        use_json_payload=True,
        path_from="nfs://192.168.10.20/srv/nfs/media",
        path_to="/mnt/nas/media",
    )
    client = oh.OppoClient(cfg)
    captured = {}

    def fake_get(endpoint, query=None, timeout=None):
        captured["endpoint"] = endpoint
        captured["query"] = query
        return "OK"

    monkeypatch.setattr(client, "_get", fake_get)
    client.play("nfs://192.168.10.20/srv/nfs/media/Gina.mp4")
    assert captured["endpoint"] == "/playnormalfile"
    assert captured["query"].startswith("payload=")
    payload = json.loads(urllib.parse.unquote(captured["query"][len("payload="):]))
    assert payload["path"] == "/mnt/nas/media/Gina.mp4"


def test_play_builds_raw_path(monkeypatch):
    cfg = Config(oppo_ip="1.2.3.4", use_json_payload=False)
    client = oh.OppoClient(cfg)
    captured = {}

    def fake_get(endpoint, query=None, timeout=None):
        captured["endpoint"] = endpoint
        captured["query"] = query
        return "OK"

    monkeypatch.setattr(client, "_get", fake_get)
    client.play("/mnt/nas/media/Gina.mp4")
    assert captured["endpoint"] == "/playnormalfile"
    assert captured["query"].startswith("path=")


def test_ensure_share_mounted_nfs(monkeypatch):
    client = oh.OppoClient(Config(oppo_ip="1.2.3.4"))
    calls = []

    def fake_get_json(endpoint, query=None, timeout=None):
        calls.append((endpoint, query))
        return {}

    monkeypatch.setattr(client, "_get_json", fake_get_json)
    client.ensure_share_mounted("nfs://192.168.10.20/srv/nfs/media/Gina.mp4")
    endpoints = [c[0] for c in calls]
    assert "/login_nfs" in endpoints
    assert "/mount_nfs" in endpoints


def test_ensure_share_mounted_local_is_noop(monkeypatch):
    client = oh.OppoClient(Config(oppo_ip="1.2.3.4"))
    calls = []
    monkeypatch.setattr(client, "_get_json", lambda *a, **k: calls.append(a) or {})
    client.ensure_share_mounted("/mnt/nas/media/Gina.mp4")
    assert calls == []


def test_translate_decodes_encoded_nfs_url():
    encoded = "nfs://192.168.10.20/srv/nfs/media/3%20Body%20Problem%20(2024)/S01E01%20-%20Countdown.mkv"
    out = oh.translate_play_path(encoded, "nfs://192.168.10.20", "")
    assert out == "/srv/nfs/media/3 Body Problem (2024)/S01E01 - Countdown.mkv"


def test_translate_literal_spaces_unchanged():
    literal = "nfs://192.168.10.20/srv/nfs/media/3 Body Problem (2024)/S01E01 - Countdown.mkv"
    out = oh.translate_play_path(literal, "nfs://192.168.10.20", "")
    assert out == "/srv/nfs/media/3 Body Problem (2024)/S01E01 - Countdown.mkv"


def test_translate_local_path_not_decoded():
    local = "/mnt/nas/media/100%/file.mkv"
    assert oh.translate_play_path(local, "nfs://x", "/y") == "/mnt/nas/media/100%/file.mkv"


def test_play_decodes_spaces_end_to_end(monkeypatch):
    cfg = Config(oppo_ip="1.2.3.4", use_json_payload=True, path_from="nfs://192.168.10.20", path_to="")
    client = oh.OppoClient(cfg)
    captured = {}
    monkeypatch.setattr(
        client, "_get", lambda endpoint, query=None, timeout=None: captured.update(query=query) or "OK"
    )
    client.play("nfs://192.168.10.20/srv/nfs/media/3%20Body%20Problem%20(2024)/S01E01.mkv")
    payload = json.loads(urllib.parse.unquote(captured["query"][len("payload="):]))
    assert payload["path"] == "/srv/nfs/media/3 Body Problem (2024)/S01E01.mkv"
