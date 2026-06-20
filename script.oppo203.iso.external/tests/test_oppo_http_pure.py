"""PR1 (Xnoppo V3 adoption): pure-HTTP/436 primitives in oppo_control.

Exercised with a mocked ``urllib.request.urlopen`` -- no real OPPO, network, or
hardware. Pins each new endpoint's URL/verb and that transport failures raise
OppoError. These primitives are function-only/unwired in PR1; the HTTP launch
orchestration wires them later.
"""

import sys
import urllib.error
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _path in (str(ROOT), str(LIB)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from resources.lib.oppo import oppo_control as oc


class FakeSettings(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self

    def get_bool(self, key, default=False):
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("1", "true", "yes", "on")


SETTINGS = FakeSettings({"oppo_ip": "10.0.0.5", "oppo_http_port": "436"})
BASE = "http://10.0.0.5:436"


class _FakeResponse:
    def __init__(self, body, status=200):
        self._body = body.encode("utf-8") if isinstance(body, str) else body
        self.status = status

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def http():
    """Patch urlopen; yield (urls, state). Stage a response via state['body'] /
    ['status'] / ['error']."""
    urls: list[str] = []
    state = {"body": "{}", "status": 200, "error": None}

    def fake_urlopen(url, timeout=None):
        urls.append(url)
        if state["error"] is not None:
            raise state["error"]
        return _FakeResponse(state["body"], state["status"])

    with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
        yield urls, state


# --- send_remote_key_http --------------------------------------------------


def test_send_remote_key_http_builds_url(http):
    urls, state = http
    state["body"] = "OK"
    assert oc.send_remote_key_http(SETTINGS, "PON") == "OK"
    assert urls[-1] == BASE + "/sendremotekey?key=PON"


def test_send_remote_key_http_rejects_empty():
    with pytest.raises(oc.OppoError):
        oc.send_remote_key_http(SETTINGS, "   ")


# --- get_global_info / global_info_is_playing ------------------------------


def test_get_global_info_parses_json(http):
    urls, state = http
    state["body"] = '{"is_playing": true, "volume": 30}'
    info = oc.get_global_info(SETTINGS)
    assert info["is_playing"] is True
    assert urls[-1] == BASE + "/getglobalinfo"


def test_get_global_info_raw_on_non_json(http):
    _, state = http
    state["body"] = "not json"
    assert oc.get_global_info(SETTINGS) == {"raw": "not json"}


def test_global_info_is_playing_bool_flag():
    assert oc.global_info_is_playing({"is_playing": True}) is True
    assert oc.global_info_is_playing({"is_playing": False}) is False


def test_global_info_is_playing_string_flag():
    assert oc.global_info_is_playing({"is_playing": "1"}) is True
    assert oc.global_info_is_playing({"is_playing": "playing"}) is True


def test_global_info_is_playing_nested_and_status_fallback():
    assert oc.global_info_is_playing({"result": {"is_playing": True}}) is True
    # no is_playing flag -> shared status heuristic (e_play_status 0 == playing)
    assert oc.global_info_is_playing({"e_play_status": 0}) is True
    assert oc.global_info_is_playing({"is_playing": False, "foo": "bar"}) is False


def test_global_info_is_playing_non_dict_is_false():
    assert oc.global_info_is_playing("nope") is False


# --- get_playing_time / get_device_list ------------------------------------


def test_get_playing_time_url(http):
    urls, state = http
    state["body"] = '{"elapsed": 12, "total": 100}'
    assert oc.get_playing_time(SETTINGS)["total"] == 100
    assert urls[-1] == BASE + "/getplayingtime"


def test_get_device_list_url(http):
    urls, state = http
    state["body"] = '{"devices": []}'
    oc.get_device_list(SETTINGS)
    assert urls[-1] == BASE + "/getdevicelist"


# --- detect_nfs ------------------------------------------------------------


def test_detect_nfs_top_flag(http):
    _, state = http
    state["body"] = '{"nfs": "1"}'
    assert oc.detect_nfs(SETTINGS) is True


def test_detect_nfs_device_type(http):
    _, state = http
    state["body"] = '{"devicelist": [{"type": "NFS-share"}]}'
    assert oc.detect_nfs(SETTINGS) is True


def test_detect_nfs_absent(http):
    _, state = http
    state["body"] = '{"devices": [{"type": "smb"}]}'
    assert oc.detect_nfs(SETTINGS) is False


def test_detect_nfs_transport_error_is_false(http):
    _, state = http
    state["error"] = urllib.error.URLError("down")
    assert oc.detect_nfs(SETTINGS) is False


def test_detect_nfs_non_dict_is_false(http):
    _, state = http
    state["body"] = "[1, 2, 3]"
    assert oc.detect_nfs(SETTINGS) is False


# --- login / share-list ----------------------------------------------------


def test_login_smb_url(http):
    urls, state = http
    state["body"] = '{"ok": 1}'
    oc.login_smb(SETTINGS, "192.168.1.2", user="u", password="p")
    assert urls[-1].startswith(BASE + "/login_smb?")
    assert "ip=192.168.1.2" in urls[-1]
    assert "user=u" in urls[-1]
    assert "password=p" in urls[-1]


def test_login_nfs_url(http):
    urls, state = http
    state["body"] = '{"ok": 1}'
    oc.login_nfs(SETTINGS, "192.168.1.3")
    assert urls[-1].startswith(BASE + "/login_nfs?")
    assert "ip=192.168.1.3" in urls[-1]


def test_list_smb_shares_strings(http):
    urls, state = http
    state["body"] = '{"shares": ["Movies", "Music"]}'
    assert oc.list_smb_shares(SETTINGS, "192.168.1.2") == ["Movies", "Music"]
    assert "/getsmbsharelist?" in urls[-1]


def test_list_nfs_shares_mixed_items(http):
    urls, state = http
    # str item, dict with name, dict with share, dict without either, non-str/dict item
    state["body"] = '{"list": ["a", {"name": "b"}, {"share": "c"}, {"z": 1}, 5]}'
    assert oc.list_nfs_shares(SETTINGS, "192.168.1.3") == ["a", "b", "c"]
    assert "/getnfssharelist?" in urls[-1]


def test_share_names_non_dict_and_missing():
    assert oc._share_names("nope") == []
    assert oc._share_names({"other": 1}) == []


# --- mount -----------------------------------------------------------------


def test_mount_smb_strips_leading_slash(http):
    urls, state = http
    state["body"] = '{"ok": 1}'
    oc.mount_smb(SETTINGS, "192.168.1.2", "/Movies", user="u", password="p")
    assert urls[-1].startswith(BASE + "/mount_smb?")
    assert "share=Movies" in urls[-1]  # leading slash stripped


def test_mount_nfs_strips_leading_slash(http):
    urls, state = http
    state["body"] = '{"ok": 1}'
    oc.mount_nfs(SETTINGS, "192.168.1.3", "/export/media")
    assert urls[-1].startswith(BASE + "/mount_nfs?")
    assert "export=export%2Fmedia" in urls[-1]


# --- check_folder_has_bdmv -------------------------------------------------


def test_check_folder_has_bdmv_true_bool(http):
    urls, state = http
    state["body"] = '{"has_bdmv": true}'
    assert oc.check_folder_has_bdmv(SETTINGS, "smb://x/Movie") is True
    assert urls[-1].startswith(BASE + "/checkfolderhasBDMV?path=")


def test_check_folder_has_bdmv_false_bool(http):
    _, state = http
    state["body"] = '{"has_bdmv": false}'
    assert oc.check_folder_has_bdmv(SETTINGS, "x") is False


def test_check_folder_has_bdmv_string_values(http):
    _, state = http
    state["body"] = '{"result": "1"}'
    assert oc.check_folder_has_bdmv(SETTINGS, "x") is True
    state["body"] = '{"hasBDMV": "0"}'
    assert oc.check_folder_has_bdmv(SETTINGS, "x") is False


def test_check_folder_has_bdmv_missing_is_false(http):
    _, state = http
    state["body"] = '{"other": 1}'
    assert oc.check_folder_has_bdmv(SETTINGS, "x") is False


def test_check_folder_has_bdmv_non_dict_is_false(http):
    _, state = http
    state["body"] = "[1, 2]"
    assert oc.check_folder_has_bdmv(SETTINGS, "x") is False


def test_check_folder_has_bdmv_transport_error_raises(http):
    _, state = http
    state["error"] = urllib.error.URLError("down")
    with pytest.raises(oc.OppoError):
        oc.check_folder_has_bdmv(SETTINGS, "x")
