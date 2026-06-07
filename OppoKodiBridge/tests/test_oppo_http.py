import socket
import urllib.parse
import urllib.request

import pytest

from resources.lib import oppo_http as oh
from resources.lib.config import Config


def test_parse_media_path_nfs():
    s, folder, fn = oh.parse_media_path(
        "nfs://192.168.1.177/mnt/Super3/Super3Share/02TV/3 Body Problem (2024)/Season 1/S01E01.mkv"
    )
    assert s == "192.168.1.177"
    assert folder == "mnt/Super3/Super3Share/02TV/3 Body Problem (2024)/Season 1"
    assert fn == "S01E01.mkv"


def test_parse_media_path_short():
    assert oh.parse_media_path("nfs://srv/share/file.mkv") == ("srv", "share", "file.mkv")
    assert oh.parse_media_path("nfs://srv/file.mkv") == ("srv", "", "file.mkv")


def test_parse_media_path_empty():
    assert oh.parse_media_path("") == ("", "", "")


def test_nfs_server_from_devices():
    devices = {
        "devicelist": [
            {"sub_type": "cifs", "name": "OPPO-PROXY"},
            {"sub_type": "nfs", "name": "192.168.10.20"},
        ]
    }
    assert oh.nfs_server_from_devices(devices) == "192.168.10.20"
    assert oh.nfs_server_from_devices({"devicelist": []}) is None
    assert oh.nfs_server_from_devices({}) is None


def test_status_is_idle():
    assert oh.status_is_idle("STOP")
    assert oh.status_is_idle("")
    assert not oh.status_is_idle("PLAY")


def test_info_is_playing_real_oppo_fields():
    idle = {
        "success": True,
        "is_video_playing": False,
        "is_audio_playing": False,
        "is_bdmv_playing": False,
        "activeapp": "scrn_svr",
    }
    assert not oh.info_is_playing(idle)
    assert oh.info_is_playing({**idle, "is_video_playing": True})
    assert oh.info_is_playing({"is_bdmv_playing": True})
    assert not oh.info_is_playing({})


def _client():
    return oh.OppoClient(Config(oppo_ip="1.2.3.4"))


def test_play_file_endpoint_shape(monkeypatch):
    client = _client()
    cap = {}
    monkeypatch.setattr(client, "_get", lambda endpoint, timeout=None: cap.update(ep=endpoint) or "{}")
    client.play_file("192.168.10.20", "3 Body Problem - S01E01.mkv", "0", nfs=True)
    ep = cap["ep"]
    assert ep.startswith("/playnormalfile?{")
    assert ep.endswith("}")
    inner = urllib.parse.unquote(ep[len("/playnormalfile?{") : -1])
    assert '"path":"/mnt/nfs1/3 Body Problem - S01E01.mkv"' in inner
    assert '"extraNetPath":"192.168.10.20"' in inner
    assert '"appDeviceType":2' in inner


def test_mount_nfs_endpoint(monkeypatch):
    client = _client()
    cap = {}
    monkeypatch.setattr(client, "_get", lambda endpoint, timeout=None: cap.update(ep=endpoint) or "{}")
    client.mount_nfs("192.168.10.20", "mnt/Super3/Super3Share/Season 1")
    ep = cap["ep"]
    assert ep.startswith('/mountNfsSharedFolder?{"server":"192.168.10.20","folder":"')
    assert "Season%201" in ep  # folder is url-encoded, slashes preserved


def test_login_and_signin_endpoints(monkeypatch):
    client = _client()
    caps = []
    monkeypatch.setattr(client, "_get", lambda endpoint, timeout=None: caps.append(endpoint) or "{}")
    client.login_nfs("192.168.10.20")
    client.signin("192.168.1.100")
    assert caps[0].startswith("/loginNfsServer?")
    assert "192.168.10.20" in urllib.parse.unquote(caps[0])
    assert caps[1].startswith("/signin?")
    decoded = urllib.parse.unquote(caps[1])
    assert "appIpAddress" in decoded and "192.168.1.100" in decoded


def test_get_raises_oppoerror_on_timeout(monkeypatch):
    client = _client()

    def boom(*a, **k):
        raise socket.timeout("timed out")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    with pytest.raises(oh.OppoError):
        client._get("/getglobalinfo")


def test_get_raises_oppoerror_on_refused(monkeypatch):
    client = _client()

    def boom(*a, **k):
        raise ConnectionRefusedError("refused")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    with pytest.raises(oh.OppoError):
        client._get("/getglobalinfo")
