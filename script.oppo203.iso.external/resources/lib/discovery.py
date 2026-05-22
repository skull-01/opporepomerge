"""Discovery improvements (v1.1.3).

mDNS + SSDP probes (alongside the existing UDP multicast), plus a
device cache and "apply preset" mapping so the wizard's IP step can
surface previously-seen devices.

All network I/O flows through injected callables so the suite is
fully unit-testable without sockets.

Public API
----------
- parse_ssdp_response(text)            -> dict | None
- parse_mdns_record(record_dict)       -> dict | None
- vendor_to_preset(vendor_string)      -> str | None
- discover(*, ssdp=None, mdns=None, udp=None,
           timeout=2.0, now=None)      -> list[Device]
- DeviceCache(path=None, fs=None, clock=None)
    .add(device), .all(), .recent(max_age_s=86400),
    .save(), .load(), .clear()
- apply_preset_for(device)             -> str | None  (preset_id or None)

Each Device dict has: ip, port, vendor, model, source ("ssdp"|"mdns"|
"udp"), last_seen (epoch float), preset (mapped via vendor_to_preset).
"""

import json
import re as _re
import time as _time

# Vendor -> preset mapping. Case-insensitive substring match.
_VENDOR_PRESETS = (
    ("oppo", "oppo203"),
    ("reavon", "reavon_x200"),
    ("magnetar", "magnetar"),
    ("zappiti", "zappiti_reference"),
    ("chinoppo", "chinoppo"),
    ("udp-203", "chinoppo"),
    ("udp-205", "chinoppo"),
)


def vendor_to_preset(vendor):
    """Map a free-form vendor/model string to a known preset_id."""
    if not vendor:
        return None
    s = str(vendor).lower()
    for needle, preset in _VENDOR_PRESETS:
        if needle in s:
            return preset
    return None


def apply_preset_for(device):
    """Return the preset_id for a device, or None if unmappable."""
    if not isinstance(device, dict):
        return None
    if device.get("preset"):
        return device["preset"]
    return vendor_to_preset(" ".join([str(device.get("vendor", "")), str(device.get("model", ""))]))


# ---------------------------------------------------------------------
# SSDP: M-SEARCH responses are HTTP-like text blocks
# ---------------------------------------------------------------------

_SSDP_HEADER_RE = _re.compile(r"^([A-Za-z0-9-]+)\s*:\s*(.*?)\s*$")


def parse_ssdp_response(text):
    """Parse an SSDP M-SEARCH response.  Returns a dict with at least
    `location`, `server`, and any other headers, or None if the text
    is not a recognisable SSDP response.
    """
    if not text:
        return None
    lines = str(text).splitlines()
    if not lines:
        return None
    if not lines[0].upper().startswith("HTTP/"):
        # Some devices reply with NOTIFY * HTTP/1.1; accept that too.
        if not lines[0].upper().startswith("NOTIFY"):
            return None
    headers = {}
    for line in lines[1:]:
        m = _SSDP_HEADER_RE.match(line)
        if m:
            headers[m.group(1).lower()] = m.group(2)
    if not headers:
        return None

    # Extract IP from LOCATION header
    ip = None
    loc = headers.get("location", "")
    m = _re.search(r"https?://([^/:]+)(?::(\d+))?", loc)
    if m:
        ip = m.group(1)

    server = headers.get("server", "")
    return {
        "ip": ip,
        "port": 23,  # control port; SSDP advertises HTTP
        "vendor": server,
        "model": headers.get("st", "") or headers.get("nt", ""),
        "source": "ssdp",
        "headers": headers,
    }


# ---------------------------------------------------------------------
# mDNS: tests pass a simplified record dict with name/type/addresses/
# properties; production wiring (e.g. zeroconf) builds the same shape.
# ---------------------------------------------------------------------


def parse_mdns_record(record):
    """Parse a normalised mDNS record into a Device dict, or None."""
    if not isinstance(record, dict):
        return None
    addrs = record.get("addresses") or []
    if not addrs:
        return None
    props = record.get("properties") or {}
    name = record.get("name", "") or ""
    return {
        "ip": addrs[0],
        "port": int(record.get("port") or 23),
        "vendor": props.get("vendor") or props.get("manufacturer") or name,
        "model": props.get("model") or record.get("type", ""),
        "source": "mdns",
        "name": name,
    }


# ---------------------------------------------------------------------
# discover(): orchestrates all three probes via injection
# ---------------------------------------------------------------------


def _now_fn(now):
    return now() if callable(now) else (now if now else _time.time())


def discover(*, ssdp=None, mdns=None, udp=None, timeout=2.0, now=None):
    """Run all configured probes concurrently (here: serially, since
    each is short-lived) and return a deduped list of Device dicts.

    Probes are callables: ssdp() -> [text...], mdns() -> [record...],
    udp() -> [(ip, vendor)...].  Missing probes are skipped silently.
    """
    seen = {}
    ts = _now_fn(now)

    def _add(dev):
        if not dev or not dev.get("ip"):
            return
        key = (dev["ip"], dev.get("port", 23))
        prev = seen.get(key)
        # Prefer the richest source; mdns/ssdp beat udp.
        priority = {"mdns": 3, "ssdp": 2, "udp": 1}
        if prev and priority.get(prev.get("source"), 0) >= priority.get(dev.get("source"), 0):
            return
        dev = dict(dev)
        dev["last_seen"] = ts
        dev["preset"] = apply_preset_for(dev)
        seen[key] = dev

    if ssdp:
        try:
            for resp in ssdp() or []:
                _add(parse_ssdp_response(resp))
        except Exception:
            pass
    if mdns:
        try:
            for rec in mdns() or []:
                _add(parse_mdns_record(rec))
        except Exception:
            pass
    if udp:
        try:
            for ip, vendor in udp() or []:
                _add({"ip": ip, "port": 23, "vendor": vendor or "", "model": "", "source": "udp"})
        except Exception:
            pass

    return sorted(seen.values(), key=lambda d: d["ip"])


# ---------------------------------------------------------------------
# DeviceCache: persistent JSON cache for the wizard's IP step
# ---------------------------------------------------------------------


class _RealFS:
    def exists(self, p):
        import os

        return os.path.exists(p)

    def read(self, p):
        with open(p, "r", encoding="utf-8") as f:
            return f.read()

    def write(self, p, t):
        import os

        d = os.path.dirname(p)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)


class DeviceCache:
    """Keeps the most recent observation per (ip, port) pair."""

    def __init__(self, path=None, fs=None, clock=None):
        self.path = path
        self.fs = fs if fs is not None else _RealFS()
        self.clock = clock if clock is not None else _time.time
        self._items = {}  # (ip,port) -> dev

    def add(self, device):
        if not isinstance(device, dict) or not device.get("ip"):
            return None
        key = (device["ip"], int(device.get("port", 23)))
        d = dict(device)
        d.setdefault("last_seen", self.clock())
        d.setdefault("preset", apply_preset_for(d))
        self._items[key] = d
        return d

    def add_many(self, devices):
        for d in devices or []:
            self.add(d)

    def all(self):
        return sorted(self._items.values(), key=lambda d: d["ip"])

    def recent(self, max_age_s=86400):
        now = self.clock()
        return [d for d in self.all() if (now - float(d.get("last_seen", 0))) <= max_age_s]

    def clear(self):
        self._items = {}

    def save(self):
        if not self.path:
            return False
        payload = {
            "version": 1,
            "items": [
                {
                    "ip": k[0],
                    "port": k[1],
                    **{kk: vv for kk, vv in v.items() if kk not in ("ip", "port")},
                }
                for k, v in self._items.items()
            ],
        }
        self.fs.write(self.path, json.dumps(payload, sort_keys=True))
        return True

    def load(self):
        if not self.path or not self.fs.exists(self.path):
            return False
        try:
            data = json.loads(self.fs.read(self.path))
        except Exception:
            return False
        items = data.get("items") if isinstance(data, dict) else None
        if not isinstance(items, list):
            return False
        self._items = {}
        for it in items:
            if not isinstance(it, dict):
                continue
            ip = it.get("ip")
            port = int(it.get("port") or 23)
            if not ip:
                continue
            self._items[(ip, port)] = it
        return True
