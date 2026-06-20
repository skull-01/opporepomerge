"""Minimal Broadlink RM4 mini client for CEC-free TV input switching.

Reimplements ONLY the four verbs OppoKodiBridge needs -- discover-by-known-IP, auth, send-IR and
learn -- from the (MIT-licensed) python-broadlink wire protocol. It deliberately does NOT depend on
upstream ``python-broadlink``: that package hard-imports the ``cryptography`` C-extension, which is
absent on CoreELEC. AES-128-CBC is sourced via a try-chain (pycryptodome fast-path -> vendored
pure-Python floor), so this module is correct whether or not the box exposes a crypto library, and
ships as one stdlib-only file inside the runtime add-on (no pip, no vendored package tree).

Protocol constants/offsets are the canonical python-broadlink ones (``device.py`` / ``remote.py``).
The device-type id read at discovery is logged as a sanity check only -- it never gates behaviour; we
hardcode RM4 length-prefixed framing because the operator's blaster is a confirmed RM4 mini.
"""
from __future__ import annotations

import base64
import binascii
import datetime
import random
import re
import socket
import struct
import time

from .kodilog import log

# Fixed key/IV used to encrypt the auth packet (before a session key exists). The IV stays fixed for
# ALL traffic; only the key changes (INIT_KEY -> per-session key) after auth().
INIT_KEY = bytes.fromhex("097628343fe99e23765c1513accf8b02")
INIT_VECT = bytes.fromhex("562e17996d093d28ddb3ba695a2e6f58")
PORT = 80

_HEX_RE = re.compile(r"^[0-9a-fA-F]+$")


# --------------------------------------------------------------------------------------------------
# AES-128 (pure-Python floor) -- table-driven, validated by a FIPS-197 known-answer test off-box.
# --------------------------------------------------------------------------------------------------
_SBOX = bytes.fromhex(
    "637c777bf26b6fc53001672bfed7ab76"
    "ca82c97dfa5947f0add4a2af9ca472c0"
    "b7fd9326363ff7cc34a5e5f171d83115"
    "04c723c31896059a071280e2eb27b275"
    "09832c1a1b6e5aa0523bd6b329e32f84"
    "53d100ed20fcb15b6acbbe394a4c58cf"
    "d0efaafb434d338545f9027f503c9fa8"
    "51a3408f929d38f5bcb6da2110fff3d2"
    "cd0c13ec5f974417c4a77e3d645d1973"
    "60814fdc222a908846eeb814de5e0bdb"
    "e0323a0a4906245cc2d3ac629195e479"
    "e7c8376d8dd54ea96c56f4ea657aae08"
    "ba78252e1ca6b4c6e8dd741f4bbd8b8a"
    "703eb5664803f60e613557b986c11d9e"
    "e1f8981169d98e949b1e87e9ce5528df"
    "8ca1890dbfe6426841992d0fb054bb16"
)
_INV_SBOX = bytes.fromhex(
    "52096ad53036a538bf40a39e81f3d7fb"
    "7ce339829b2fff87348e4344c4dee9cb"
    "547b9432a6c2233dee4c950b42fac34e"
    "082ea16628d924b2765ba2496d8bd125"
    "72f8f66486689816d4a45ccc5d65b692"
    "6c704850fdedb9da5e154657a78d9d84"
    "90d8ab008cbcd30af7e45805b8b34506"
    "d02c1e8fca3f0f02c1afbd0301138a6b"
    "3a9111414f67dcea97f2cfcef0b4e673"
    "96ac7422e7ad3585e2f937e81c75df6e"
    "47f11a711d29c5896fb7620eaa18be1b"
    "fc563e4bc6d279209adbc0fe78cd5af4"
    "1fdda8338807c731b11210592780ec5f"
    "60517fa919b54a0d2de57a9f93c99cef"
    "a0e03b4dae2af5b0c8ebbb3c83539961"
    "172b047eba77d626e169146355210c7d"
)
_RCON = (0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36)


def _gmul(a: int, b: int) -> int:
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return p & 0xFF


def _expand_key(key: bytes) -> bytes:
    rk = bytearray(key)  # 16 bytes -> 176 bytes (11 round keys)
    rcon_i = 1
    while len(rk) < 176:
        t = bytearray(rk[-4:])
        if len(rk) % 16 == 0:
            t = t[1:] + t[:1]                      # RotWord
            t = bytes(_SBOX[x] for x in t)         # SubWord
            t = bytes([t[0] ^ _RCON[rcon_i]]) + t[1:]
            rcon_i += 1
        for i in range(4):
            rk.append(rk[-16] ^ t[i])
    return bytes(rk)


def _shift_rows(s):
    o = bytearray(16)
    for row in range(4):
        for c in range(4):
            o[row + 4 * c] = s[row + 4 * ((c + row) % 4)]
    return o


def _inv_shift_rows(s):
    o = bytearray(16)
    for row in range(4):
        for c in range(4):
            o[row + 4 * c] = s[row + 4 * ((c - row) % 4)]
    return o


def _mix_columns(s):
    o = bytearray(16)
    for c in range(4):
        a0, a1, a2, a3 = s[4 * c], s[4 * c + 1], s[4 * c + 2], s[4 * c + 3]
        o[4 * c] = _gmul(a0, 2) ^ _gmul(a1, 3) ^ a2 ^ a3
        o[4 * c + 1] = a0 ^ _gmul(a1, 2) ^ _gmul(a2, 3) ^ a3
        o[4 * c + 2] = a0 ^ a1 ^ _gmul(a2, 2) ^ _gmul(a3, 3)
        o[4 * c + 3] = _gmul(a0, 3) ^ a1 ^ a2 ^ _gmul(a3, 2)
    return o


def _inv_mix_columns(s):
    o = bytearray(16)
    for c in range(4):
        a0, a1, a2, a3 = s[4 * c], s[4 * c + 1], s[4 * c + 2], s[4 * c + 3]
        o[4 * c] = _gmul(a0, 14) ^ _gmul(a1, 11) ^ _gmul(a2, 13) ^ _gmul(a3, 9)
        o[4 * c + 1] = _gmul(a0, 9) ^ _gmul(a1, 14) ^ _gmul(a2, 11) ^ _gmul(a3, 13)
        o[4 * c + 2] = _gmul(a0, 13) ^ _gmul(a1, 9) ^ _gmul(a2, 14) ^ _gmul(a3, 11)
        o[4 * c + 3] = _gmul(a0, 11) ^ _gmul(a1, 13) ^ _gmul(a2, 9) ^ _gmul(a3, 14)
    return o


class _Aes128:
    """Pure-Python AES-128, raw blocks + CBC (no padding). The guaranteed floor of the try-chain."""

    def __init__(self, key: bytes):
        if len(key) != 16:
            raise ValueError("AES-128 needs a 16-byte key, got {}".format(len(key)))
        self._rk = _expand_key(key)

    def encrypt_block(self, block: bytes) -> bytes:
        rk = self._rk
        s = bytearray(block[i] ^ rk[i] for i in range(16))
        for rnd in range(1, 10):
            for i in range(16):
                s[i] = _SBOX[s[i]]
            s = _shift_rows(s)
            s = _mix_columns(s)
            for i in range(16):
                s[i] ^= rk[16 * rnd + i]
        for i in range(16):
            s[i] = _SBOX[s[i]]
        s = _shift_rows(s)
        for i in range(16):
            s[i] ^= rk[160 + i]
        return bytes(s)

    def decrypt_block(self, block: bytes) -> bytes:
        rk = self._rk
        s = bytearray(block[i] ^ rk[160 + i] for i in range(16))
        for rnd in range(9, 0, -1):
            s = _inv_shift_rows(s)
            for i in range(16):
                s[i] = _INV_SBOX[s[i]]
            for i in range(16):
                s[i] ^= rk[16 * rnd + i]
            s = _inv_mix_columns(s)
        s = _inv_shift_rows(s)
        for i in range(16):
            s[i] = _INV_SBOX[s[i]]
        for i in range(16):
            s[i] ^= rk[i]
        return bytes(s)

    def cbc(self, iv: bytes, data: bytes, *, encrypt: bool) -> bytes:
        out = bytearray()
        prev = iv
        if encrypt:
            for i in range(0, len(data), 16):
                blk = bytes(x ^ y for x, y in zip(data[i:i + 16], prev))
                enc = self.encrypt_block(blk)
                out += enc
                prev = enc
        else:
            for i in range(0, len(data), 16):
                blk = data[i:i + 16]
                dec = self.decrypt_block(blk)
                out += bytes(x ^ y for x, y in zip(dec, prev))
                prev = blk
        return bytes(out)


def _aes_cbc(key: bytes, iv: bytes, data: bytes, *, encrypt: bool) -> bytes:
    """Raw (no-pad) AES-128-CBC. Broadlink zero-pads to 16 manually and parses replies by inner
    length, so callers pad before encrypt and never depad on decrypt. Fast path uses pycryptodome
    (``Crypto`` namespace, present on CoreELEC) when importable; otherwise the pure-Python floor."""
    try:
        from Crypto.Cipher import AES as _AES  # pycryptodome / pycrypto

        cipher = _AES.new(key, _AES.MODE_CBC, iv)
        return cipher.encrypt(data) if encrypt else cipher.decrypt(data)
    except Exception:  # noqa: BLE001 - any import/runtime failure falls through to the floor
        return _Aes128(key).cbc(iv, data, encrypt=encrypt)


# --------------------------------------------------------------------------------------------------
# Wire protocol
# --------------------------------------------------------------------------------------------------
def _checksum(buf: bytes) -> int:
    return (sum(buf) + 0xBEAF) & 0xFFFF


def decode_ir_code(token: str) -> bytes:
    """Decode a stored IR code -> raw ``0x26...`` blob. Accepts base64 (the SmartIR/IRDB ecosystem
    default that the learn tool emits) OR hex. Hex is detected FIRST when the token is an even-length
    pure-hex string, so a code like ``2600...`` is never mis-read as base64."""
    t = (token or "").strip()
    if not t:
        raise ValueError("empty IR code")
    if len(t) % 2 == 0 and _HEX_RE.match(t):
        return binascii.unhexlify(t)
    return base64.b64decode(t, validate=True)  # binascii.Error is a ValueError subclass


class RM4:
    def __init__(self, ip: str, *, port: int = PORT, timeout: float = 4.0):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.devtype = 0
        self.mac = b"\x00" * 6           # stored in discovery byte-order; header wants it reversed
        self.dev_id = b"\x00\x00\x00\x00"
        self.key = INIT_KEY              # swapped to the session key after auth()
        self.count = random.randint(0x8000, 0xFFFF)

    # ---- public verbs ----------------------------------------------------------------------------
    def discover(self) -> "RM4":
        """Unicast the 48-byte hello to ip:80 (the IP is known, so no broadcast) and read the
        device type + MAC needed to frame every later packet."""
        pkt = bytearray(0x30)
        now = datetime.datetime.now()
        tz = int(time.timezone / -3600)
        if tz < 0:
            pkt[0x08] = (0xFF + tz - 1) & 0xFF
            pkt[0x09] = pkt[0x0A] = pkt[0x0B] = 0xFF
        else:
            pkt[0x08] = tz & 0xFF
        pkt[0x0C] = now.year & 0xFF
        pkt[0x0D] = (now.year >> 8) & 0xFF
        pkt[0x0E] = now.minute
        pkt[0x0F] = now.hour
        pkt[0x10] = now.year % 100
        pkt[0x11] = now.isoweekday()
        pkt[0x12] = now.day
        pkt[0x13] = now.month
        octets = self._local_ip().split(".")
        if len(octets) == 4:
            for n, val in enumerate(octets):
                pkt[0x18 + n] = int(val) & 0xFF
        pkt[0x26] = 0x06
        c = _checksum(pkt)
        pkt[0x20] = c & 0xFF
        pkt[0x21] = (c >> 8) & 0xFF
        resp = self._udp(bytes(pkt))
        self.devtype = resp[0x34] | (resp[0x35] << 8)
        self.mac = bytes(resp[0x3A:0x40])
        log("RM4 sanity: devtype=0x%04x mac=%s" % (self.devtype, self.mac[::-1].hex(":")))
        return self

    def auth(self) -> "RM4":
        payload = bytearray(0x50)
        payload[0x04:0x13] = b"\x31" * 15
        payload[0x1E] = 0x01
        payload[0x2D] = 0x01
        payload[0x30:0x30 + 14] = b"OppoKodiBridge"
        reply = self._send_packet(0x65, bytes(payload))
        dec = _aes_cbc(INIT_KEY, INIT_VECT, reply[0x38:], encrypt=False)
        self.dev_id = bytes(dec[0x00:0x04])
        self.key = bytes(dec[0x04:0x14])            # 16-byte session key
        return self

    def send_ir(self, blob: bytes, repeat: int = 0) -> bool:
        """Blast a raw ``0x26`` IR blob. ``repeat`` sets the in-packet repeat byte -- safe ONLY for a
        single discrete (idempotent) code, never for a sequenced key. Refuses non-IR (RF) blobs."""
        blob = bytes(blob)
        if not blob or blob[0] != 0x26:
            raise ValueError(
                "not an IR (0x26) code (lead={!r}); RF (0xb2/0xd7) is not supported".format(blob[:1])
            )
        if repeat:
            blob = blob[:1] + bytes([repeat & 0xFF]) + blob[2:]
        inner = struct.pack("<HI", len(blob) + 4, 0x02) + blob
        self._send_packet(0x6A, inner)
        return True                                  # ack = blaster emitted; the TV never acks

    def enter_learning(self) -> None:
        self._send_packet(0x6A, struct.pack("<HI", 4, 0x03))

    def check_learned(self):
        reply = self._send_packet(0x6A, struct.pack("<HI", 4, 0x04))
        dec = _aes_cbc(self.key, INIT_VECT, reply[0x38:], encrypt=False)
        p_len = dec[0] | (dec[1] << 8)
        body = bytes(dec[0x06:p_len + 2])
        return body or None

    # ---- framing ---------------------------------------------------------------------------------
    def _send_packet(self, cmd: int, payload: bytes) -> bytes:
        self.count = (self.count + 1) & 0xFFFF
        hdr = bytearray(0x38)
        hdr[0:8] = b"\x5a\xa5\xaa\x55\x5a\xa5\xaa\x55"
        hdr[0x24] = self.devtype & 0xFF
        hdr[0x25] = (self.devtype >> 8) & 0xFF
        hdr[0x26] = cmd & 0xFF
        hdr[0x27] = (cmd >> 8) & 0xFF
        hdr[0x28] = self.count & 0xFF
        hdr[0x29] = (self.count >> 8) & 0xFF
        hdr[0x2A:0x30] = self.mac[::-1]
        hdr[0x30:0x34] = self.dev_id
        p_ck = _checksum(payload)
        hdr[0x34] = p_ck & 0xFF
        hdr[0x35] = (p_ck >> 8) & 0xFF
        pad = (-len(payload)) % 16
        enc = _aes_cbc(self.key, INIT_VECT, bytes(payload) + b"\x00" * pad, encrypt=True)
        pkt = bytearray(bytes(hdr) + enc)
        w_ck = _checksum(pkt)
        pkt[0x20] = w_ck & 0xFF
        pkt[0x21] = (w_ck >> 8) & 0xFF
        return self._udp(bytes(pkt))

    def _udp(self, data: bytes) -> bytes:
        last = None
        for _ in range(2):                           # one bounded resend absorbs a dropped datagram
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            try:
                sock.sendto(data, (self.ip, self.port))
                resp, _addr = sock.recvfrom(2048)
                return resp
            except socket.timeout as exc:
                last = exc
            finally:
                sock.close()
        raise OSError("no reply from RM4 at {}:{} ({})".format(self.ip, self.port, last))

    def _local_ip(self) -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect((self.ip, self.port))
            return sock.getsockname()[0]
        except OSError:
            return "0.0.0.0"
        finally:
            sock.close()
