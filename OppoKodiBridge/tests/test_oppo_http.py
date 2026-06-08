import socket
import urllib.parse
import urllib.request

import pytest

from resources.lib import oppo_http as oh
from resources.lib.config import Config

KODI = (
    "nfs://192.168.1.177/mnt/Super3/Super3Share/02TV/01Series/02-MKV/"
    "3 Body Problem (2024)/Season 1/3 Body Problem - S01E01 - Countdown.mkv"
)
FROM = "nfs://192.168.1.177/mnt/Super3/Super3Share"


def test_split_share_relative():
    folder, base = oh.split_share_relative(KODI, FROM)
    assert folder == "02TV/01Series/02-MKV/3 Body Problem (2024)/Season 1"
    assert base == "3 Body Problem - S01E01 - Countdown.mkv"


def test_split_share_relative_urlencoded():
    enc = "nfs://192.168.1.177/mnt/Super3/Super3Share/A%20B/file%20(2024).mkv"
    folder, base = oh.split_share_relative(enc, FROM)
    assert folder == "A B"
    assert base == "file (2024).mkv"


def test_split_share_relative_no_match():
    assert oh.split_share_relative("nfs://other/x/y.mkv", FROM) == (None, None)


def test_split_share_relative_root_file():
    folder, base = oh.split_share_relative(FROM + "/movie.mkv", FROM)
    assert folder == ""
    assert base == "movie.mkv"


def test_oppo_mount_folder():
    assert (
        oh.oppo_mount_folder("02TV/01Series/Season 1", "srv/nfs/media")
        == "srv/nfs/media/02TV/01Series/Season 1"
    )
    assert oh.oppo_mount_folder("", "srv/nfs/media") == "srv/nfs/media"
    assert oh.oppo_mount_folder("A/B", "/srv/nfs/media/") == "srv/nfs/media/A/B"


def test_nfs_server_from_devices():
    devices = {
        "devicelist": [
            {"sub_type": "cifs", "name": "OPPO-PROXY"},
            {"sub_type": "nfs", "name": "192.168.10.20"},
        ]
    }
    assert oh.nfs_server_from_devices(devices) == "192.168.10.20"
    assert oh.nfs_server_from_devices({"devicelist": []}) is None


def test_status_is_idle():
    assert oh.status_is_idle("STOP")
    assert oh.status_is_idle("")
    assert not oh.status_is_idle("PLAY")


def test_info_is_playing_real_fields():
    idle = {"success": True, "is_video_playing": False, "is_audio_playing": False, "activeapp": "scrn_svr"}
    assert not oh.info_is_playing(idle)
    assert oh.info_is_playing({**idle, "is_video_playing": True})
    assert oh.info_is_playing({"is_bdmv_playing": True})
    assert not oh.info_is_playing({})


def _client():
    return oh.OppoClient(Config(oppo_ip="1.2.3.4"))


def test_play_file_endpoint(monkeypatch):
    client = _client()
    cap = {}
    monkeypatch.setattr(client, "_get_json", lambda ep, timeout=None: cap.update(ep=ep) or {})
    client.play_file("192.168.10.20", "3 Body Problem - S01E01.mkv")
    ep = cap["ep"]
    assert ep.startswith("/playnormalfile?{") and ep.endswith("}")
    inner = urllib.parse.unquote(ep[len("/playnormalfile?{") : -1])
    assert '"path":"/mnt/nfs1/3 Body Problem - S01E01.mkv"' in inner
    assert '"extraNetPath":"192.168.10.20"' in inner


def test_mount_nfs_endpoint(monkeypatch):
    client = _client()
    cap = {}
    monkeypatch.setattr(client, "_get_json", lambda ep, timeout=None: cap.update(ep=ep) or {})
    client.mount_nfs("192.168.10.20", "srv/nfs/media/Season 1")
    ep = cap["ep"]
    assert ep.startswith('/mountNfsSharedFolder?{"server":"192.168.10.20","folder":"')
    assert "Season%201" in ep


def test_login_and_signin_endpoints(monkeypatch):
    client = _client()
    caps = []
    monkeypatch.setattr(client, "_get_json", lambda ep, timeout=None: caps.append(ep) or {})
    monkeypatch.setattr(client, "_get", lambda ep, timeout=None: caps.append(ep) or "ok")
    client.login_nfs("192.168.10.20")
    client.signin("192.168.1.100")
    assert any(c.startswith("/loginNfsServer?") and "192.168.10.20" in urllib.parse.unquote(c) for c in caps)
    assert any(c.startswith("/signin?") and "appIconType" in urllib.parse.unquote(c) for c in caps)


def test_get_raises_oppoerror_on_timeout(monkeypatch):
    client = _client()

    def boom(*a, **k):
        raise socket.timeout("timed out")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    with pytest.raises(oh.OppoError):
        client._get("/getglobalinfo")


def test_is_disc_path():
    assert oh.is_disc_path("01Movies/Ant-Man (2015)/BDMV/index.bdmv")
    assert oh.is_disc_path("x/VIDEO_TS/VIDEO_TS.IFO")
    assert not oh.is_disc_path("02TV/Show/S01E01.mkv")
    assert not oh.is_disc_path("01Movies/Crouching Tiger (2000).iso")


def test_is_iso():
    assert oh.is_iso("01Movies/Crouching Tiger (2000).iso")
    assert oh.is_iso("X/Y.ISO")
    assert not oh.is_iso("02TV/Show/S01E01.mkv")
    assert not oh.is_iso("X/disc/BDMV/index.bdmv")


def test_is_oppo_target():
    # Disc images and disc folders -> OPPO.
    assert oh.is_oppo_target(FROM + "/01Movies/Dune (2021).iso")
    assert oh.is_oppo_target("01Movies/Ant-Man (2015)/BDMV/index.bdmv")
    assert oh.is_oppo_target(FROM + "/01Movies/Ant-Man (2015)/BDMV/STREAM/00800.m2ts")
    assert oh.is_oppo_target("X/VIDEO_TS/VIDEO_TS.IFO")
    assert oh.is_oppo_target(FROM + "/01Movies/Dune%20(2021).iso")  # url-encoded
    # Everything else stays in Kodi.
    assert not oh.is_oppo_target(KODI)
    assert not oh.is_oppo_target(FROM + "/01Movies/film.mp4")
    assert not oh.is_oppo_target("Movies/looseclip/STREAM/0080.m2ts")  # no BDMV folder


def test_disc_folder():
    assert (
        oh.disc_folder("01Movies/01-4kDisc/Ant-Man (2015)/BDMV/index.bdmv")
        == "01Movies/01-4kDisc/Ant-Man (2015)"
    )
    assert oh.disc_folder("x/VIDEO_TS/VIDEO_TS.IFO") == "x"


def test_play_bdmv_endpoint(monkeypatch):
    client = _client()
    cap = {}
    monkeypatch.setattr(client, "_get_json", lambda ep, timeout=None: cap.update(ep=ep) or {})
    client.play_bdmv("Ant-Man (2015)")
    ep = cap["ep"]
    assert ep.startswith('/checkfolderhasBDMV?{"folderpath":"/mnt/nfs1/')
    assert "Ant-Man" in urllib.parse.unquote(ep)
