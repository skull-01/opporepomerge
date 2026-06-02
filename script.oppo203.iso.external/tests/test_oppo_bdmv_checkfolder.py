"""PR6 (Xnoppo V3 adoption): resolve_disc_play_path -- the checkfolderhasBDMV-first decision.

The off path is byte-identical to today's _disc_folder_root behaviour; the only change is that a
**capable** player can be asked /checkfolderhasBDMV for a BDMV marker and, if it reports no BDMV,
the original marker path is handed over instead of the folder root. Every uncertainty (toggle off,
not capable, probe unreachable) falls back to the folder root. check_folder_has_bdmv /
_supports_http_api are patched so no real OPPO is contacted.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _p in (str(ROOT), str(LIB)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

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


BDMV = "/nas/Movie/BDMV/index.bdmv"
VIDEO_TS = "/nas/DVD/VIDEO_TS/VIDEO_TS.IFO"


def test_disc_folder_root_off_returns_original():
    assert (
        oc.resolve_disc_play_path(FakeSettings({"oppo_http_disc_folder_root": "false"}), BDMV)
        == BDMV
    )


def test_non_marker_returns_original():
    assert (
        oc.resolve_disc_play_path(FakeSettings({}), "/nas/Movie/film.mkv") == "/nas/Movie/film.mkv"
    )


def test_video_ts_folder_is_never_probed(monkeypatch):
    probed = []
    monkeypatch.setattr(oc, "check_folder_has_bdmv", lambda s, f: probed.append(f) or True)
    monkeypatch.setattr(oc, "_supports_http_api", lambda s: True)
    s = FakeSettings({"oppo_bdmv_checkfolder": "true"})
    assert oc.resolve_disc_play_path(s, VIDEO_TS) == "/nas/DVD"  # non-BDMV disc folder, unchanged
    assert probed == []


def test_bdmv_checkfolder_off_returns_folder_no_probe(monkeypatch):
    probed = []
    monkeypatch.setattr(oc, "check_folder_has_bdmv", lambda s, f: probed.append(f) or True)
    monkeypatch.setattr(oc, "_supports_http_api", lambda s: True)
    s = FakeSettings({"oppo_bdmv_checkfolder": "false"})
    assert oc.resolve_disc_play_path(s, BDMV) == "/nas/Movie"
    assert probed == []  # toggle off -> frozen behaviour, no network


def test_bdmv_not_capable_returns_folder_no_probe(monkeypatch):
    probed = []
    monkeypatch.setattr(oc, "check_folder_has_bdmv", lambda s, f: probed.append(f) or True)
    monkeypatch.setattr(oc, "_supports_http_api", lambda s: False)
    s = FakeSettings({"oppo_bdmv_checkfolder": "true"})
    assert oc.resolve_disc_play_path(s, BDMV) == "/nas/Movie"
    assert probed == []  # player not HTTP-capable -> frozen behaviour


def test_bdmv_probe_true_uses_folder(monkeypatch):
    monkeypatch.setattr(oc, "check_folder_has_bdmv", lambda s, f: True)
    monkeypatch.setattr(oc, "_supports_http_api", lambda s: True)
    assert (
        oc.resolve_disc_play_path(FakeSettings({"oppo_bdmv_checkfolder": "true"}), BDMV)
        == "/nas/Movie"
    )


def test_bdmv_probe_false_uses_original_marker(monkeypatch):
    monkeypatch.setattr(oc, "check_folder_has_bdmv", lambda s, f: False)
    monkeypatch.setattr(oc, "_supports_http_api", lambda s: True)
    assert oc.resolve_disc_play_path(FakeSettings({"oppo_bdmv_checkfolder": "true"}), BDMV) == BDMV


def test_bdmv_probe_unreachable_falls_back_to_folder(monkeypatch):
    def boom(_s, _f):
        raise oc.OppoError("down")

    monkeypatch.setattr(oc, "check_folder_has_bdmv", boom)
    monkeypatch.setattr(oc, "_supports_http_api", lambda s: True)
    assert (
        oc.resolve_disc_play_path(FakeSettings({"oppo_bdmv_checkfolder": "true"}), BDMV)
        == "/nas/Movie"
    )


def test_translate_media_path_routes_through_resolver(monkeypatch):
    # Integration: _translate_media_path uses resolve_disc_play_path, so a no-BDMV verdict hands
    # over the original marker (then path translation / urlencode apply on top).
    monkeypatch.setattr(oc, "check_folder_has_bdmv", lambda s, f: False)
    monkeypatch.setattr(oc, "_supports_http_api", lambda s: True)
    s = FakeSettings({"oppo_bdmv_checkfolder": "true", "oppo_http_urlencode_path": "false"})
    assert oc._translate_media_path(s, BDMV) == BDMV


def test_build_json_payload_routes_through_resolver(monkeypatch):
    monkeypatch.setattr(oc, "check_folder_has_bdmv", lambda s, f: True)
    monkeypatch.setattr(oc, "_supports_http_api", lambda s: True)
    s = FakeSettings({"oppo_bdmv_checkfolder": "true"})
    assert oc._build_json_payload(s, BDMV)["path"] == "/nas/Movie"


def test_supports_http_api_reads_model_capability():
    assert oc._supports_http_api(FakeSettings({"oppo_hardware_model": "udp_203"})) is True
    assert oc._supports_http_api(FakeSettings({"oppo_hardware_model": "chinoppo_m9205"})) is False
    assert oc._supports_http_api(FakeSettings({})) is False
