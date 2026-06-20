"""The monitor: poll until playing, then hold the verbose channel until stop; give up if playback
never starts. Asserts nothing about CEC -- it only observes."""
from resources.lib import monitor
from resources.lib.config import Config


class _Client:
    def __init__(self, plays_on=1):
        self.n = 0
        self.plays_on = plays_on
        self.verbose = 0

    def is_playing(self):
        self.n += 1
        return self.n >= self.plays_on

    def verbose_watch_until_stop(self, should_abort):
        self.verbose += 1
        return True


def test_watch_playback_observes_start_then_verbose(monkeypatch):
    monkeypatch.setattr(monitor, "interruptible_sleep", lambda *a, **k: None)
    client = _Client(plays_on=1)
    cfg = Config(oppo_ip="x", poll_interval=2, idle_confirmations=2)
    assert monitor.watch_playback(cfg, client) is True
    assert client.verbose == 1


def test_watch_playback_gives_up_if_never_starts(monkeypatch):
    monkeypatch.setattr(monitor, "interruptible_sleep", lambda *a, **k: None)

    class Never:
        def is_playing(self):
            return False

        def verbose_watch_until_stop(self, should_abort):
            raise AssertionError("verbose must not open if playback never started")

    cfg = Config(oppo_ip="x", poll_interval=2, idle_confirmations=2)  # grace = max(2, 10) = 10 polls
    assert monitor.watch_playback(cfg, Never()) is False


def test_watch_playback_aborts(monkeypatch):
    monkeypatch.setattr(monitor, "interruptible_sleep", lambda *a, **k: None)
    cfg = Config(oppo_ip="x")
    assert monitor.watch_playback(cfg, _Client(plays_on=999), should_abort=lambda: True) is False
