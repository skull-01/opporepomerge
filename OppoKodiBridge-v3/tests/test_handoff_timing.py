"""Off-box tests for the handoff timing change: the play-side IR switch must fire AFTER the OPPO
reports playing (not before wake), and the interim power-cycle must run ONLY when IR is not
configured. The daemon IR thread is made synchronous so ordering is deterministic."""
from resources.lib import config as config_mod
from resources.lib import handoff
from resources.lib import ir

ISO = "nfs://h/share/01Movies/Dune (2021).iso"


class _FakeClient:
    """Records the call order of the lifecycle-significant methods; reports playing on first poll."""

    def __init__(self, config):
        self.order = []
        self._polls = 0

    def power_cycle(self, *a, **k):
        self.order.append("power_cycle")

    def wake_and_wait(self, *a, **k):
        self.order.append("wake")
        return True

    def get_firmware_version(self):
        return ""

    def get_setup_menu(self):
        return ""

    def signin(self, app_ip):
        return ""

    def get_global_info(self):
        return {}

    def get_device_list(self):
        return {}

    def get_nfs_share_list(self):
        return ""

    def login_nfs(self, server):
        return {}

    def mount_nfs(self, server, folder):
        self.order.append("mount")
        return {}

    def play_file(self, server, name):
        self.order.append("play")
        return {"success": True}

    def play_bdmv(self, name):
        self.order.append("play")
        return {"success": True}

    def stop(self):
        return {}

    def is_playing(self):
        self._polls += 1
        return True                     # playing on the first poll -> _watch_playback breaks at once

    def verbose_watch_until_stop(self, should_abort):
        self.order.append("verbose")


class _SyncThread:
    """Drop-in for threading.Thread that runs the target synchronously on start()."""

    def __init__(self, target=None, name=None, daemon=None):
        self._target = target

    def start(self):
        if self._target:
            self._target()

    def join(self, *a, **k):
        pass


def _wire(monkeypatch, order_sink):
    captured = {}

    def make_client(config):
        client = _FakeClient(config)
        client.order = order_sink
        captured["client"] = client
        return client

    monkeypatch.setattr(handoff, "OppoClient", make_client)
    monkeypatch.setattr(handoff, "nfs_server_from_devices", lambda d: "192.168.10.20")
    monkeypatch.setattr(handoff, "local_ip_toward", lambda ip, port: "127.0.0.1")
    monkeypatch.setattr(handoff, "_interruptible_sleep", lambda *a, **k: None)
    monkeypatch.setattr(handoff.threading, "Thread", _SyncThread)
    monkeypatch.setattr(ir, "switch_to_oppo", lambda c: order_sink.append("ir_oppo") or True)
    monkeypatch.setattr(ir, "switch_to_kodi", lambda c: order_sink.append("ir_kodi") or True)
    return captured


def test_ir_fires_after_play_not_before_wake(monkeypatch):
    order = []
    _wire(monkeypatch, order)
    cfg = config_mod.Config(
        oppo_ip="1.2.3.4",
        path_from="nfs://h/share",
        path_to="srv/nfs/media",
        broadlink_ip="9.9.9.9",
        ir_code_oppo="AAAA",
        ir_code_kodi="BBBB",
    )
    handoff.play_on_oppo(cfg, ISO)
    assert "power_cycle" not in order             # IR configured -> no interim power-cycle
    assert order.index("ir_oppo") > order.index("wake")
    assert order.index("ir_oppo") > order.index("play")
    assert order.index("ir_oppo") < order.index("verbose")   # fired before the verbose watch opens
    assert order[-1] == "ir_kodi"                 # reclaim to Kodi is last


def test_power_cycle_only_when_ir_not_configured(monkeypatch):
    order = []
    _wire(monkeypatch, order)
    cfg = config_mod.Config(
        oppo_ip="1.2.3.4",
        path_from="nfs://h/share",
        path_to="srv/nfs/media",
        grab_tv_on_play=True,
        # no broadlink_ip / ir_code_oppo -> ir.configured() is False
    )
    handoff.play_on_oppo(cfg, ISO)
    assert order[0] == "power_cycle"              # interim grab happens up front, before wake
    assert order.index("power_cycle") < order.index("wake")
    assert "ir_oppo" not in order and "ir_kodi" not in order
