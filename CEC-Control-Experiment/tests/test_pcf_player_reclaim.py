"""The external player must request the single-shot reclaim once, on stop -- success OR failure -- and
never when the reclaim is disabled."""
import pcf_player
from resources.lib.config import Config


def _wire(monkeypatch, cfg, play=lambda c, f: True):
    calls = {"n": 0, "dir": None}
    monkeypatch.setattr(pcf_player.handoff, "play_on_oppo", play)
    monkeypatch.setattr(pcf_player, "_load_config", lambda: cfg)
    monkeypatch.setattr(pcf_player, "_data_dir", lambda: "/tmp/cec")

    def fake_request(d):
        calls["n"] += 1
        calls["dir"] = d
        return True

    monkeypatch.setattr(pcf_player.cec_reclaim, "request", fake_request)
    return calls


def test_reclaim_requested_once_on_normal_stop(monkeypatch):
    calls = _wire(monkeypatch, Config(cec_reclaim_on_stop=True))
    assert pcf_player.main(["pcf_player.py", "nfs://h/share/x.iso"]) == 0
    assert calls["n"] == 1 and calls["dir"] == "/tmp/cec"


def test_reclaim_requested_even_when_handoff_raises(monkeypatch):
    def boom(cfg, kodi_file):
        raise RuntimeError("handoff blew up")

    calls = _wire(monkeypatch, Config(cec_reclaim_on_stop=True), play=boom)
    assert pcf_player.main(["pcf_player.py", "f"]) == 1   # rc=1 on handoff error...
    assert calls["n"] == 1                                # ...but the reclaim still fires (finally)


def test_no_reclaim_when_disabled(monkeypatch):
    calls = _wire(monkeypatch, Config(cec_reclaim_on_stop=False))
    assert pcf_player.main(["pcf_player.py", "f"]) == 0
    assert calls["n"] == 0
