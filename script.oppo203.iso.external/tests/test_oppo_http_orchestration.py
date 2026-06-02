"""PR3 (Xnoppo V3 adoption): pure-HTTP launch orchestration in external_player._start_oppo_http.

The oppo_control HTTP primitives are replaced with recording fakes -- no real OPPO, network, or
time. Pins the sequence (wake -> signin -> best-effort mount -> disc-aware play -> confirm), the
SMB/NFS mount routing, the one-shot ISO auto-heal, the BDMV probe, and that every enrichment step
is non-fatal so the launch degrades to the proven play.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _p in (str(ROOT), str(LIB)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import external_player as ep  # bare name -> resources.lib.kodi.external_player

from resources.lib.kodi import settings_reader as sr


class Ctl:
    def __init__(self):
        self.calls: list[str] = []
        self.playing = True
        self.nfs = False
        self.play_raises = False
        self.mount_raises = False
        self.confirm_raises = False


def _install_oc(monkeypatch, ctl):
    def record(name):
        def fn(_settings, *_a, **_k):
            ctl.calls.append(name)
            return {}

        return fn

    def play(_settings, _media_file):
        ctl.calls.append("play")
        if ctl.play_raises:
            raise RuntimeError("play failed")
        return "@OK"

    def mount_smb(_settings, *_a, **_k):
        ctl.calls.append("mount_smb")
        if ctl.mount_raises:
            raise RuntimeError("mount failed")
        return {}

    def get_global_info(_settings):
        ctl.calls.append("get_global_info")
        if ctl.confirm_raises:
            raise RuntimeError("no info")
        return {"is_playing": ctl.playing}

    fns = {
        "activate_http_api": lambda _s: ctl.calls.append("activate"),
        "signin_http_api": lambda _s: ctl.calls.append("signin") or "",
        "send_remote_key_http": lambda _s, key: ctl.calls.append(f"key:{key}") or "OK",
        "detect_nfs": lambda _s: (ctl.calls.append("detect_nfs"), ctl.nfs)[1],
        "login_smb": record("login_smb"),
        "login_nfs": record("login_nfs"),
        "mount_smb": mount_smb,
        "mount_nfs": record("mount_nfs"),
        "check_folder_has_bdmv": lambda _s, _f: ctl.calls.append("check_bdmv") or False,
        "get_global_info": get_global_info,
        "global_info_is_playing": lambda info: bool(
            isinstance(info, dict) and info.get("is_playing")
        ),
        "play_media_http_api": play,
    }
    # Patch the exact oppo_control module object _start_oppo_http resolves via
    # _oppo_control_module(); under a serial run the ENH-#43 stub-context tests purge + re-import
    # oppo_control, so patching it by name (importlib) can miss the live object.
    oc = ep._oppo_control_module()
    for fn_name, fn in fns.items():
        monkeypatch.setattr(oc, fn_name, fn, raising=False)
    monkeypatch.setattr(ep, "log", lambda m: None)
    monkeypatch.setattr(ep.time, "sleep", lambda *_a: None)


def _settings(**over):
    return sr.Settings(over)


def test_smb_iso_orchestration_order(monkeypatch):
    ctl = Ctl()
    _install_oc(monkeypatch, ctl)
    ep._start_oppo_http(_settings(), "smb://10.0.1.10/MyNAS/film.iso")
    assert ctl.calls[:3] == ["activate", "key:PON", "signin"]  # wake before signin
    assert "mount_smb" in ctl.calls
    assert ctl.calls.index("mount_smb") < ctl.calls.index("play")  # mount before play


def test_local_path_skips_mount(monkeypatch):
    ctl = Ctl()
    _install_oc(monkeypatch, ctl)
    ep._start_oppo_http(_settings(), "/mnt/nfs1/film.iso")
    assert "login_smb" not in ctl.calls
    assert "mount_smb" not in ctl.calls
    assert "mount_nfs" not in ctl.calls
    assert "play" in ctl.calls


def test_nfs_scheme_uses_nfs_mount(monkeypatch):
    ctl = Ctl()
    _install_oc(monkeypatch, ctl)
    ep._start_oppo_http(_settings(), "nfs://10.0.1.10/export/film.iso")
    assert "login_nfs" in ctl.calls
    assert "mount_nfs" in ctl.calls
    assert "mount_smb" not in ctl.calls


def test_smb_with_detect_nfs_uses_nfs(monkeypatch):
    ctl = Ctl()
    ctl.nfs = True
    _install_oc(monkeypatch, ctl)
    ep._start_oppo_http(_settings(), "smb://10.0.1.10/share/film.iso")
    assert "mount_nfs" in ctl.calls
    assert "mount_smb" not in ctl.calls


def test_mount_failure_is_nonfatal(monkeypatch):
    ctl = Ctl()
    ctl.mount_raises = True
    _install_oc(monkeypatch, ctl)
    ep._start_oppo_http(_settings(), "smb://10.0.1.10/share/film.iso")  # must not raise
    assert "play" in ctl.calls


def test_iso_autoheal_resends_when_not_playing(monkeypatch):
    ctl = Ctl()
    ctl.playing = False
    _install_oc(monkeypatch, ctl)
    ep._start_oppo_http(_settings(), "smb://10.0.1.10/share/film.iso")
    assert ctl.calls.count("play") == 2  # original + auto-heal replay
    assert "key:STP" in ctl.calls


def test_iso_autoheal_skips_when_playing(monkeypatch):
    ctl = Ctl()
    ctl.playing = True
    _install_oc(monkeypatch, ctl)
    ep._start_oppo_http(_settings(), "smb://10.0.1.10/share/film.iso")
    assert ctl.calls.count("play") == 1
    assert "key:STP" not in ctl.calls


def test_iso_autoheal_disabled(monkeypatch):
    ctl = Ctl()
    ctl.playing = False
    _install_oc(monkeypatch, ctl)
    ep._start_oppo_http(_settings(oppo_http_iso_autoheal="false"), "smb://10.0.1.10/share/film.iso")
    assert ctl.calls.count("play") == 1
    assert "key:STP" not in ctl.calls


def test_iso_autoheal_skips_when_unconfirmable(monkeypatch):
    ctl = Ctl()
    ctl.confirm_raises = True
    _install_oc(monkeypatch, ctl)
    ep._start_oppo_http(_settings(), "smb://10.0.1.10/share/film.iso")
    assert ctl.calls.count("play") == 1  # cannot confirm -> no resend
    assert "key:STP" not in ctl.calls


def test_bdmv_path_probes_checkfolder(monkeypatch):
    ctl = Ctl()
    _install_oc(monkeypatch, ctl)
    ep._start_oppo_http(_settings(), "smb://10.0.1.10/share/Movie/BDMV/index.bdmv")
    assert "check_bdmv" in ctl.calls
    assert ctl.calls.count("play") == 1  # BDMV path: no ISO auto-heal
    assert "key:STP" not in ctl.calls


def test_normal_path_no_bdmv_no_autoheal(monkeypatch):
    ctl = Ctl()
    ctl.playing = False
    _install_oc(monkeypatch, ctl)
    ep._start_oppo_http(_settings(), "smb://10.0.1.10/share/movie.mkv")
    assert "check_bdmv" not in ctl.calls
    assert ctl.calls.count("play") == 1  # not an ISO -> no auto-heal even when not playing


def test_launch_is_nonfatal_on_play_failure(monkeypatch):
    ctl = Ctl()
    ctl.play_raises = True
    logs: list[str] = []
    _install_oc(monkeypatch, ctl)
    monkeypatch.setattr(ep, "log", lambda m: logs.append(m))
    ep._start_oppo_http(_settings(), "smb://10.0.1.10/share/film.iso")  # must not raise
    assert any("HTTP handoff failed" in m for m in logs)


def test_parse_network_share_helper():
    assert ep._parse_network_share("smb://10.0.1.10/MyNAS/x.iso") == ("smb", "10.0.1.10", "MyNAS")
    assert ep._parse_network_share("nfs://srv/export/x.iso") == ("nfs", "srv", "export")
    assert ep._parse_network_share("/mnt/local/x.iso") is None
    assert ep._parse_network_share("smb://onlyserver") is None
