"""Off-box tests for the hand-rolled Broadlink RM4 client: AES (FIPS-197 KAT), packet framing,
code decoding, and a full discover/auth/send/learn round-trip against a fake in-process UDP server.
No hardware, no RM4."""
import base64
import socket
import struct
import threading

import pytest

from resources.lib import broadlink_rm4 as bl


# --- AES floor: FIPS-197 known-answer + no-PKCS7 + try-chain parity ---------------------------------
def test_aes_fips197_block():
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    pt = bytes.fromhex("00112233445566778899aabbccddeeff")
    ct = bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a")
    aes = bl._Aes128(key)
    assert aes.encrypt_block(pt) == ct
    assert aes.decrypt_block(ct) == pt


def test_aes_cbc_roundtrip_floor():
    data = bytes(range(32))
    enc = bl._Aes128(bl.INIT_KEY).cbc(bl.INIT_VECT, data, encrypt=True)
    assert enc != data
    assert bl._Aes128(bl.INIT_KEY).cbc(bl.INIT_VECT, enc, encrypt=False) == data


def test_aes_cbc_no_pkcs7_padding():
    # a single 16-byte block must encrypt to exactly 16 bytes (no extra PKCS#7 pad block)
    out = bl._aes_cbc(bl.INIT_KEY, bl.INIT_VECT, b"\x00" * 16, encrypt=True)
    assert len(out) == 16


def test_aes_trychain_matches_floor():
    # whichever backend the try-chain takes (pycryptodome or the floor) must agree with the floor
    data = bytes(range(16))
    assert bl._aes_cbc(bl.INIT_KEY, bl.INIT_VECT, data, encrypt=True) == bl._Aes128(
        bl.INIT_KEY
    ).cbc(bl.INIT_VECT, data, encrypt=True)


# --- checksum + code decoding ----------------------------------------------------------------------
def test_checksum():
    assert bl._checksum(b"\x00\x00") == 0xBEAF
    assert bl._checksum(b"\x01\x02") == (0xBEAF + 3) & 0xFFFF


def test_decode_hex_and_base64_equivalent():
    blob = bytes([0x26, 0x00, 0x04, 0x00, 0x01, 0x02, 0x0D, 0x05])
    assert bl.decode_ir_code(blob.hex()) == blob
    assert bl.decode_ir_code(base64.b64encode(blob).decode()) == blob


def test_decode_prefers_hex_for_ambiguous_pure_hex():
    # "2600" is valid base64 AND valid hex; hex-first must win so the byte 0x26 is preserved
    assert bl.decode_ir_code("2600") == bytes([0x26, 0x00])


def test_decode_bad_raises_valueerror():
    with pytest.raises(ValueError):
        bl.decode_ir_code("!!! not valid !!!")
    with pytest.raises(ValueError):
        bl.decode_ir_code("")


# --- send framing + RF rejection -------------------------------------------------------------------
def _stub_client(monkeypatch, capture):
    dev = bl.RM4("1.2.3.4")
    dev.devtype = 0x649B
    dev.mac = bytes([0x11, 0x22, 0x33, 0x44, 0x55, 0x66])
    dev.dev_id = b"\x01\x02\x03\x04"
    dev.key = bl.INIT_KEY

    def fake_udp(data):
        capture["req"] = data
        return b"\x00" * 0x38 + bl._aes_cbc(dev.key, bl.INIT_VECT, b"\x00" * 16, encrypt=False)

    monkeypatch.setattr(dev, "_udp", fake_udp)
    return dev


def test_send_ir_framing(monkeypatch):
    cap = {}
    dev = _stub_client(monkeypatch, cap)
    blob = bytes([0x26, 0x00, 0x04, 0x00, 0x01, 0x02, 0x0D, 0x05])
    dev.send_ir(blob, repeat=0)
    req = cap["req"]
    assert req[0:8] == b"\x5a\xa5\xaa\x55\x5a\xa5\xaa\x55"      # magic
    assert req[0x26] == 0x6A and req[0x27] == 0x00              # command 0x6a
    inner = bl._aes_cbc(dev.key, bl.INIT_VECT, req[0x38:], encrypt=False)
    assert inner[0:2] == struct.pack("<H", len(blob) + 4)       # length-prefix
    assert inner[2:6] == struct.pack("<I", 0x02)               # send-IR sub-command
    assert inner[6:6 + len(blob)] == blob


def test_send_ir_repeat_byte_only_mutates_byte1(monkeypatch):
    cap = {}
    dev = _stub_client(monkeypatch, cap)
    blob = bytes([0x26, 0x00, 0x02, 0x00, 0xAA, 0xBB, 0x0D, 0x05])
    dev.send_ir(blob, repeat=1)
    inner = bl._aes_cbc(dev.key, bl.INIT_VECT, cap["req"][0x38:], encrypt=False)
    sent = inner[6:6 + len(blob)]
    assert sent[0] == 0x26 and sent[1] == 0x01                  # repeat byte set, lead intact


def test_send_ir_rejects_rf_and_empty():
    dev = bl.RM4("1.2.3.4")
    with pytest.raises(ValueError):
        dev.send_ir(bytes([0xB2, 0x00, 0x00, 0x00]))           # RF433 lead -> rejected
    with pytest.raises(ValueError):
        dev.send_ir(b"")


# --- full round-trip against a fake RM4 UDP server -------------------------------------------------
class _FakeRM4:
    """In-process RM4 over UDP on 127.0.0.1:<ephemeral>. Drive ``RM4(ip, port=...)`` at it."""

    SID = b"\xaa\xbb\xcc\xdd"
    SKEY = bytes(range(16, 32))
    LEARNED = bytes([0x26, 0x00, 0x02, 0x00, 0xAA, 0xBB, 0x0D, 0x05])

    def __init__(self, devtype=0x649B, mac=bytes([0x11, 0x22, 0x33, 0x44, 0x55, 0x66])):
        self.devtype = devtype
        self.mac = mac
        self.sent = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 0))
        self.port = self.sock.getsockname()[1]
        self._stop = False
        self._t = threading.Thread(target=self._serve, daemon=True)
        self._t.start()

    def _serve(self):
        self.sock.settimeout(0.3)
        while not self._stop:
            try:
                data, addr = self.sock.recvfrom(2048)
            except socket.timeout:
                continue
            except OSError:
                break
            if len(data) >= 0x30 and data[0x26] == 0x06:
                self.sock.sendto(self._hello(), addr)
            else:
                cmd = data[0x26] | (data[0x27] << 8)
                self.sock.sendto(self._reply(cmd, data), addr)

    def _hello(self):
        r = bytearray(0x40)
        r[0x34] = self.devtype & 0xFF
        r[0x35] = (self.devtype >> 8) & 0xFF
        r[0x3A:0x40] = self.mac
        return bytes(r)

    def _enc(self, pt):
        return bl._aes_cbc(self.SKEY, bl.INIT_VECT, pt + b"\x00" * ((-len(pt)) % 16), encrypt=True)

    def _reply(self, cmd, req):
        hdr = bytearray(0x38)
        hdr[0x26] = cmd & 0xFF
        hdr[0x27] = (cmd >> 8) & 0xFF
        if cmd == 0x65:
            pt = bytearray(0x14)
            pt[0:4] = self.SID
            pt[4:20] = self.SKEY
            enc = bl._aes_cbc(bl.INIT_KEY, bl.INIT_VECT, bytes(pt) + b"\x00" * 12, encrypt=True)
            return bytes(hdr) + enc
        dec = bl._aes_cbc(self.SKEY, bl.INIT_VECT, req[0x38:], encrypt=False)
        self.sent.append(bytes(dec))
        sub = dec[2] | (dec[3] << 8)
        if sub == 0x04:  # check_learned -> hand back a canned blob (p_len = len+4)
            pt = bytes([len(self.LEARNED) + 4, 0, 0, 0, 0, 0]) + self.LEARNED
            return bytes(hdr) + self._enc(pt)
        return bytes(hdr) + self._enc(b"\x00" * 16)

    def close(self):
        self._stop = True
        self.sock.close()


def test_fake_rm4_full_roundtrip():
    srv = _FakeRM4(devtype=0x649B)
    try:
        dev = bl.RM4("127.0.0.1", port=srv.port, timeout=2.0).discover().auth()
        assert dev.devtype == 0x649B
        assert dev.mac == srv.mac
        assert dev.dev_id == _FakeRM4.SID
        assert dev.key == _FakeRM4.SKEY

        blob = bytes([0x26, 0x00, 0x04, 0x00, 0x01, 0x02, 0x0D, 0x05])
        dev.send_ir(blob, repeat=0)
        inner = srv.sent[-1]
        assert inner[0:2] == struct.pack("<H", len(blob) + 4)
        assert inner[2:6] == struct.pack("<I", 0x02)
        assert inner[6:6 + len(blob)] == blob

        dev.enter_learning()
        assert dev.check_learned() == _FakeRM4.LEARNED
    finally:
        srv.close()


def test_unreachable_raises_oserror():
    # nothing is listening on this port -> bounded resend then OSError (which ir._send catches)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    dead_port = sock.getsockname()[1]
    sock.close()
    with pytest.raises(OSError):
        bl.RM4("127.0.0.1", port=dead_port, timeout=0.2).discover()
