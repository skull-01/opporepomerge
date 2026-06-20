import importlib
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for item in (str(ROOT), str(LIB)):
    if item not in sys.path:
        sys.path.insert(0, item)

import intercept


def test_should_intercept_tagged_4k_iso_sources():
    assert intercept.should_intercept_4k_disc_source("/Movies/Dune 2021 4K UHD.iso")
    assert intercept.should_intercept_4k_disc_source("/Movies/Dune 2021 2160p.iso")
    assert intercept.should_intercept_4k_disc_source("smb://server/Movies/DUNE UHD.ISO")


def test_should_intercept_tagged_bdmv_navigation_sources():
    assert intercept.should_intercept_4k_disc_source("/Movies/Dune 4K UHD/BDMV/index.bdmv")
    assert intercept.should_intercept_4k_disc_source("/Movies/Dune 2160p/BDMV/MovieObject.bdmv")
    assert intercept.should_intercept_4k_disc_source(
        "nfs://nas/Movies/Dune UHD/BDMV/PLAYLIST/00800.mpls"
    )


def test_untagged_disc_sources_use_kodi_default_player():
    assert not intercept.should_intercept_4k_disc_source("/Movies/Dune.iso")
    assert not intercept.should_intercept_4k_disc_source("/Movies/Dune/BDMV/index.bdmv")
    assert not intercept.should_intercept_4k_disc_source("/Movies/Dune/BDMV/PLAYLIST/00800.mpls")


def test_loose_and_raw_video_files_are_always_excluded():
    excluded = (
        ".mkv",
        ".mp4",
        ".m4v",
        ".mov",
        ".mpg",
        ".mpeg",
        ".avi",
        ".wmv",
        ".flv",
        ".webm",
        ".ts",
        ".m2ts",
        ".mts",
        ".m2t",
        ".vob",
        ".ogm",
        ".ogv",
        ".divx",
        ".xvid",
        ".3gp",
        ".3g2",
        ".f4v",
        ".rm",
        ".rmvb",
        ".asf",
    )
    for ext in excluded:
        assert not intercept.should_intercept_4k_disc_source(f"/Movies/Dune 4K UHD{ext}")
    assert not intercept.should_intercept_4k_disc_source("/Movies/Dune UHD/BDMV/STREAM/00001.m2ts")


def test_non_disc_tagged_paths_use_kodi_default_player():
    assert not intercept.should_intercept_4k_disc_source("/Movies/Dune 4K UHD.txt")
    assert not intercept.should_intercept_4k_disc_source("/Movies/Dune 2160p.nfo")
    assert not intercept.should_intercept_4k_disc_source("")
    assert not intercept.should_intercept_4k_disc_source(None)


def test_service_interception_uses_4k_classifier_for_new_build():
    service = importlib.import_module("service")
    assert service._should_intercept_4k_disc_source("/Movies/Dune 4K UHD.iso")
    assert not service._should_intercept_4k_disc_source("/Movies/Dune.iso")
    assert not service._should_intercept_4k_disc_source("/Movies/Dune 4K UHD.mkv")


def test_service_handle_started_ignores_untagged_and_excluded_paths():
    service = importlib.import_module("service")
    cls = service.InterceptionPlayer
    inst = cls.__new__(cls)
    inst.settings = {"addon_data_dir": ""}
    inst._active_thread = None
    fake_player = mock.MagicMock()
    fake_player.getPlayingFile.return_value = "/Movies/Dune 4K UHD.mkv"
    fake_xbmc = mock.MagicMock()
    fake_xbmc.Player.return_value = fake_player
    with (
        mock.patch.object(service, "xbmc", fake_xbmc),
        mock.patch.object(service.threading, "Thread") as thread_cls,
    ):
        inst._handle_started()
    thread_cls.assert_not_called()
