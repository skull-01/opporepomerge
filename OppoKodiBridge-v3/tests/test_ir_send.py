"""Off-box tests for the ir.py sequencing / reliability layer. The Broadlink client is monkeypatched
so no socket is touched; we assert ordering, gaps, the discrete-vs-sequence repeat rule, the honest
bool, and the bounded one-retry on a stale session."""
import pytest

from resources.lib import broadlink_rm4, ir
from resources.lib.config import Config

_BLOB = bytes([0x26, 0x00, 0x01, 0x00, 0x0D, 0x05])


class _FakeDev:
    def __init__(self):
        self.sent = []
        self.auths = 0

    def discover(self):
        return self

    def auth(self):
        self.auths += 1
        return self

    def send_ir(self, blob, repeat=0):
        self.sent.append((bytes(blob), repeat))
        return True


def _patch(monkeypatch, dev, decode=lambda t: _BLOB):
    monkeypatch.setattr(broadlink_rm4, "RM4", lambda ip, timeout=4.0: dev)
    monkeypatch.setattr(broadlink_rm4, "decode_ir_code", decode)


def test_single_discrete_code_uses_repeat(monkeypatch):
    dev = _FakeDev()
    _patch(monkeypatch, dev)
    cfg = Config(oppo_ip="x", broadlink_ip="1.2.3.4", ir_code_oppo="AAAA")
    assert ir.switch_to_oppo(cfg) is True
    assert len(dev.sent) == 1
    assert dev.sent[0][1] == ir.IR_REPEAT          # repeat enabled for a lone discrete code


def test_sequence_disables_repeat_and_gaps(monkeypatch):
    dev = _FakeDev()
    sleeps = []
    _patch(monkeypatch, dev)
    monkeypatch.setattr(ir.time, "sleep", lambda s: sleeps.append(s))
    cfg = Config(oppo_ip="x", broadlink_ip="1.2.3.4", ir_code_oppo="A, B , C")
    assert ir.switch_to_oppo(cfg) is True
    assert [r for _, r in dev.sent] == [0, 0, 0]   # repeat OFF for every key of a sequence
    assert len(dev.sent) == 3
    assert len(sleeps) == 2                          # gap between keys, not after the last
    assert all(abs(s - ir.IR_KEY_GAP_MS / 1000.0) < 1e-9 for s in sleeps)


def test_empty_code_is_noop_false():
    cfg = Config(oppo_ip="x", broadlink_ip="1.2.3.4", ir_code_oppo="AAAA")  # ir_code_kodi == ""
    assert ir.switch_to_kodi(cfg) is False


def test_unreachable_returns_false(monkeypatch):
    class _Dead:
        def discover(self):
            raise OSError("no route to host")

    monkeypatch.setattr(broadlink_rm4, "RM4", lambda ip, timeout=4.0: _Dead())
    cfg = Config(oppo_ip="x", broadlink_ip="9.9.9.9", ir_code_oppo="AAAA")
    assert ir.switch_to_oppo(cfg) is False


def test_bad_code_returns_false(monkeypatch):
    dev = _FakeDev()

    def boom(_t):
        raise ValueError("not base64/hex")

    _patch(monkeypatch, dev, decode=boom)
    cfg = Config(oppo_ip="x", broadlink_ip="1.2.3.4", ir_code_oppo="@@@")
    assert ir.switch_to_oppo(cfg) is False
    assert dev.sent == []


def test_rf_code_returns_false(monkeypatch):
    dev = _FakeDev()

    def send_rf(blob, repeat=0):
        raise ValueError("not an IR (0x26) code")

    _patch(monkeypatch, dev)
    monkeypatch.setattr(dev, "send_ir", send_rf)
    cfg = Config(oppo_ip="x", broadlink_ip="1.2.3.4", ir_code_oppo="AAAA")
    assert ir.switch_to_oppo(cfg) is False


def test_one_reauth_retry_on_stale_session(monkeypatch):
    class _Flaky(_FakeDev):
        def __init__(self):
            super().__init__()
            self.calls = 0

        def send_ir(self, blob, repeat=0):
            self.calls += 1
            if self.calls == 1:
                raise OSError("stale session")
            self.sent.append((bytes(blob), repeat))
            return True

    dev = _Flaky()
    _patch(monkeypatch, dev)
    cfg = Config(oppo_ip="x", broadlink_ip="1.2.3.4", ir_code_oppo="AAAA")
    assert ir.switch_to_oppo(cfg) is True
    assert dev.calls == 2                            # first send failed, one retry succeeded
    assert dev.auths == 2                            # initial auth + one re-auth


def test_ir_configured_predicate_is_independent_of_cfg_configured():
    assert ir.configured(Config(oppo_ip="x", broadlink_ip="1.2.3.4", ir_code_oppo="AAAA"))
    assert not ir.configured(Config(oppo_ip="x", broadlink_ip="1.2.3.4"))   # no OPPO code
    assert not ir.configured(Config(oppo_ip="x", ir_code_oppo="AAAA"))      # no blaster IP
    # cfg.configured (OPPO-IP truthiness) is a different predicate from ir.configured
    cfg = Config(oppo_ip="x")
    assert cfg.configured and not ir.configured(cfg)
