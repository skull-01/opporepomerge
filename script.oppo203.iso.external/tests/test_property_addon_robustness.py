"""Property/fuzz robustness tests for add-on coercion + framing helpers.

This is the v0.9.4 add-on property-test pass. It adds regression coverage for a cluster of
``int()``-coercion crashes a fuzz sweep surfaced in the discovery + AutoScript helpers: a
device-cache JSON file, an mDNS record, or a JSON-loaded AutoScript preset could carry a port
that is textual ("8060/tcp") or a non-finite float (``inf``), and the historical
``int(value or 23)`` turned that into a ValueError/OverflowError -- defeating the
graceful-degradation contract of functions whose whole job is to recover from junk. Same root
cause the earlier play-status pass fixed in oppo_control/i18n (an ``except`` missing
``OverflowError``); see ``resources/lib/oppo/oppo_control.py``.

It also pins two invariants as guards even though they were already robust: the eISCP frame
round-trip (``parse(build(p)) == p[:160]``) and the Kodi/player path-normalize idempotence
(``f(f(x)) == f(x)``).

Mirrors ``test_property_http_hdmi.py``: Hypothesis is used when installed; otherwise the same
invariants run against a curated deterministic sample so the gate never silently weakens.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _path in (str(ROOT), str(LIB)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from resources.lib.avr import avr_onkyo_eiscp as eiscp
from resources.lib.oppo import autoscript_helper as ash
from resources.lib.oppo import discovery as disco
from resources.lib.oppo import path_mapper as pm

try:
    from hypothesis import given
    from hypothesis import settings as hyp_settings
    from hypothesis import strategies as st

    HAVE_HYPOTHESIS = True
except ImportError:  # pragma: no cover - only on minimal images without Hypothesis
    HAVE_HYPOTHESIS = False


# A cross-section of "weird but legal" port values. Textual ports, inf/-inf/nan, and huge ints
# specifically exercise the int() coercion that previously raised. Falsy values must map to the
# default (the old ``or 23`` behavior); everything else either parses or degrades to the default.
JUNK_PORTS = (
    None,
    "",
    "   ",
    0,
    0.0,
    False,
    [],
    {},
    "23",
    "  80  ",
    8060,
    23.0,
    True,
    "x",
    "8060/tcp",
    "inf",
    "-",
    "0x10",
    "²",  # superscript two: str, not a decimal digit
    float("inf"),
    float("-inf"),
    float("nan"),
    10**40,
    -5,
    object(),
)


def test_safe_port_never_raises_and_returns_int():
    for value in JUNK_PORTS:
        out = disco._safe_port(value)
        assert isinstance(out, int), f"_safe_port({value!r}) -> {out!r}"
    # falsy -> default (matches the historical ``or 23``); valid numerics preserved.
    assert disco._safe_port(None) == 23
    assert disco._safe_port(0) == 23
    assert disco._safe_port("") == 23
    # previously-crashing inputs now degrade to the default instead of raising.
    assert disco._safe_port("8060/tcp") == 23
    assert disco._safe_port(float("inf")) == 23
    assert disco._safe_port(float("nan")) == 23
    # parseable values are preserved exactly (no behavior change on the happy path).
    assert disco._safe_port("8080") == 8080
    assert disco._safe_port(8080) == 8080
    assert disco._safe_port(5, default=9) == 5
    assert disco._safe_port("nope", default=9) == 9


def test_parse_mdns_record_never_raises():
    records = (
        None,
        "x",
        5,
        [],
        {},
        {"addresses": []},
        {"addresses": ["1.2.3.4"]},
        {"addresses": ["1.2.3.4"], "port": "8060/tcp"},
        {"addresses": ["1.2.3.4"], "port": float("inf")},
        {"addresses": ["1.2.3.4"], "port": None},
        {"addresses": ["1.2.3.4"], "port": "5555", "properties": {"vendor": "OPPO"}},
    )
    for rec in records:
        out = disco.parse_mdns_record(rec)
        assert out is None or (isinstance(out, dict) and isinstance(out["port"], int))
    # the textual/inf ports that used to raise now fall back to the default control port.
    assert disco.parse_mdns_record({"addresses": ["1.2.3.4"], "port": "8060/tcp"})["port"] == 23
    assert disco.parse_mdns_record({"addresses": ["1.2.3.4"], "port": float("inf")})["port"] == 23
    assert disco.parse_mdns_record({"addresses": ["1.2.3.4"], "port": "5555"})["port"] == 5555


class _MemFS:
    """Minimal in-memory _FS double for DeviceCache.load()/save()."""

    def __init__(self, blob: str = "") -> None:
        self._blob = blob

    def exists(self, path: str) -> bool:
        return True

    def read(self, path: str) -> str:
        return self._blob

    def write(self, path: str, data: str) -> None:
        self._blob = data


def test_device_cache_add_and_load_tolerate_junk_port():
    cache = disco.DeviceCache()
    # add() must not raise on a textual/inf port (it is documented to return dict|None).
    assert cache.add({"ip": "1.2.3.4", "port": "x"}) is not None
    assert cache.add({"ip": "1.2.3.5", "port": float("inf")}) is not None
    assert cache.add({"ip": "1.2.3.6", "port": 8060}) is not None
    assert cache.add({"not": "ip"}) is None

    # load() returns a bool and recovers (never raises) from a cache whose port is junk.
    blob = '{"version":1,"items":[{"ip":"1.2.3.4","port":"x"},{"ip":"1.2.3.5","port":99}]}'
    c2 = disco.DeviceCache(path="cache.json", fs=_MemFS(blob))
    assert c2.load() is True
    assert len(c2.all()) == 2


def test_safe_int_never_raises():
    values = (
        None,
        "",
        "x",
        "inf",
        "5",
        5,
        5.9,
        True,
        [],
        object(),
        float("inf"),
        float("-inf"),
        float("nan"),
        10**40,
    )
    for value in values:
        assert isinstance(ash._safe_int(value, 2323), int), f"_safe_int({value!r})"
    # inf used to raise OverflowError (int(float("inf"))); now degrades to the default.
    assert ash._safe_int(float("inf"), 2323) == 2323
    assert ash._safe_int("nan", 2323) == 2323
    assert ash._safe_int("8080", 2323) == 8080
    assert ash._safe_int(7, 2323) == 7


def test_generate_never_raises_and_is_shell():
    option_sets = (
        None,
        {},
        {"telnet_port": float("inf")},
        {"adb_port": float("-inf"), "enable_adb": True},
        {"mount_type": "cifs", "mount_remote": "//nas/share", "cifs_user": "u", "cifs_pass": "p"},
        {"mount_type": "nfs", "mount_remote": "nas:/export"},
        {"enable_telnet": False, "passwordless_root": False, "heartbeat_path": ""},
        {"telnet_port": "2323", "mount_type": "bogus"},
    )
    for opts in option_sets:
        out = ash.generate(opts)
        assert isinstance(out, str)
        assert out.startswith("#!/bin/sh")
        assert out.rstrip().endswith("exit 0")


# --- eISCP frame round-trip ---------------------------------------------------------------------
VALID_EISCP_PAYLOADS = ("!1PWR01", "!1SLI01", "!1PWRQSTN", "A", "x" * 159, "x" * 160, "y" * 200)


def test_eiscp_frame_round_trip():
    for payload in VALID_EISCP_PAYLOADS:
        frame = eiscp.build_eiscp_frame(payload)
        assert isinstance(frame, bytes)
        # parse strips CR/LF and caps at 160 chars; a valid payload round-trips to payload[:160].
        assert eiscp.parse_eiscp_response(frame) == payload[:160]


def test_eiscp_build_rejects_invalid_payloads():
    for bad in ("", " x", "x ", "a\rb", "a\nb"):
        with pytest.raises(ValueError):
            eiscp.build_eiscp_frame(bad)


def test_eiscp_parse_only_raises_valueerror_on_malformed_bytes():
    samples = (
        b"",
        b"ISCP",
        b"XXXX" + b"\x00" * 12,
        b"ISCP" + b"\x00" * 200,
        bytes(range(40)),
    )
    for raw in samples:
        try:
            out = eiscp.parse_eiscp_response(raw)
            assert isinstance(out, str)
        except ValueError:
            pass  # documented malformed-response signal; any other exception fails the test


# --- path normalize idempotence -----------------------------------------------------------------
NORM_INPUTS = (
    "",
    "/",
    "//",
    "/a//b/",
    "smb://host/share//x",
    "smb://h/a%20b",
    "C:\\Users\\x\\Movie.mkv",
    "nfs://h/p?q=1#frag",
    "   /trim/  ",
    "smb://h",
    "smb://h/",
    "a/b/../c",
)


def test_normalize_kodi_path_idempotent_no_decode():
    for path in NORM_INPUTS:
        once = pm.normalize_kodi_path(path, decode_url=False)
        twice = pm.normalize_kodi_path(once, decode_url=False)
        assert isinstance(once, str)
        assert twice == once, (
            f"normalize_kodi_path not idempotent for {path!r}: {once!r} -> {twice!r}"
        )
    # None is tolerated and normalizes to "".
    assert pm.normalize_kodi_path(None, decode_url=False) == ""


def test_normalize_player_path_idempotent():
    for path in NORM_INPUTS:
        once = pm.normalize_player_path(path)
        assert pm.normalize_player_path(once) == once


if HAVE_HYPOTHESIS:
    _PORTISH = st.one_of(
        st.none(),
        st.booleans(),
        st.integers(),
        st.floats(allow_nan=True, allow_infinity=True),
        st.text(max_size=12),
        st.binary(max_size=8),
    )

    @hyp_settings(max_examples=250)
    @given(value=_PORTISH)
    def test_safe_port_property(value):
        assert isinstance(disco._safe_port(value), int)

    @hyp_settings(max_examples=250)
    @given(value=_PORTISH)
    def test_safe_int_property(value):
        assert isinstance(ash._safe_int(value, 2323), int)

    @hyp_settings(max_examples=200)
    @given(port=_PORTISH, addr=st.text(max_size=20))
    def test_parse_mdns_record_property(port, addr):
        rec = {"addresses": [addr] if addr else [], "port": port}
        out = disco.parse_mdns_record(rec)
        assert out is None or isinstance(out["port"], int)

    @hyp_settings(max_examples=200)
    @given(
        opts=st.dictionaries(
            st.text(max_size=16),
            st.one_of(
                st.none(),
                st.booleans(),
                st.integers(),
                st.floats(allow_nan=True, allow_infinity=True),
                st.text(max_size=20),
            ),
            max_size=8,
        )
    )
    def test_generate_property(opts):
        out = ash.generate(opts)
        assert isinstance(out, str) and out.startswith("#!/bin/sh")

    # Printable ASCII (33..126) has no whitespace and no CR/LF, so build_eiscp_frame accepts it.
    _PAYLOAD = st.text(
        alphabet=st.characters(min_codepoint=33, max_codepoint=126), min_size=1, max_size=200
    )

    @hyp_settings(max_examples=200)
    @given(payload=_PAYLOAD)
    def test_eiscp_round_trip_property(payload):
        frame = eiscp.build_eiscp_frame(payload)
        assert eiscp.parse_eiscp_response(frame) == payload[:160]
