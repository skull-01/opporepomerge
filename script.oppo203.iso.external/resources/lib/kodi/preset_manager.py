"""Hardware preset extensibility (v1.1.4).

Loads built-in presets from playercorefactory_merge.PRESETS, merges
in user-defined presets from addon_data/custom_presets.json (custom
wins on key collision), provides a "Submit your preset" export
helper, and a firmware_min check that warns when a device runs older
firmware than the preset requires.

Public API
----------
- BUILTIN_PRESETS                            -> dict
- load_custom(path, fs=None)                 -> dict (or {} if missing/bad)
- merged_presets(custom_path=None, fs=None)  -> dict (built-ins + custom)
- export_submission(preset_id, ip=None, quirks=None, contact=None,
                    user_preset=None)        -> dict (JSON-ready)
- save_submission(submission, root_dir, *, now=None, fs=None)
                                              -> str (path written)
- compare_versions(a, b)                     -> -1 | 0 | 1 | None
- firmware_warning(preset, device_firmware)  -> str | None
"""

import json
import os
import posixpath
import re as _re
import time as _time

# Pull built-ins from the v1.1.2 player-core-factory module so there
# is exactly one source of truth.
try:
    from . import playercorefactory_merge as _pcf
except Exception:
    import playercorefactory_merge as _pcf  # tests run with sys.path tweaks


# Re-export for callers who don't want to reach into _pcf
BUILTIN_PRESETS = dict(_pcf.PRESETS)


# ---------------------------------------------------------------------
# Filesystem injection (mirrors discovery / pcf style)
# ---------------------------------------------------------------------


class _RealFS:
    def exists(self, p):
        return os.path.exists(p)

    def read(self, p):
        with open(p, "r", encoding="utf-8") as f:
            return f.read()

    def write(self, p, t):
        d = os.path.dirname(p)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)


# ---------------------------------------------------------------------
# load_custom
# ---------------------------------------------------------------------

_REQUIRED_KEYS = ("label", "start_commands", "stop_commands")


def _validate_preset(p):
    if not isinstance(p, dict):
        return False
    for k in _REQUIRED_KEYS:
        if k not in p or not isinstance(p[k], str) or not p[k]:
            return False
    if "firmware_min" in p and not isinstance(p["firmware_min"], str):
        return False
    return True


def load_custom(path, fs=None):
    """Load custom presets from a JSON file.

    Schema:
        {"presets": {"<id>": {"label":..., "start_commands":...,
                              "stop_commands":..., "firmware_min": "..."} }}

    Bad/missing files return {} silently; bad individual presets are
    skipped (the rest of the file still loads).
    """
    fs = fs if fs is not None else _RealFS()
    if not path or not fs.exists(path):
        return {}
    try:
        data = json.loads(fs.read(path))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    items = data.get("presets")
    if not isinstance(items, dict):
        return {}
    out = {}
    for pid, p in items.items():
        if not isinstance(pid, str) or not pid:
            continue
        if _validate_preset(p):
            out[pid] = dict(p)
    return out


# ---------------------------------------------------------------------
# merged_presets
# ---------------------------------------------------------------------


def merged_presets(custom_path=None, fs=None):
    """Return BUILTIN_PRESETS overlaid with valid custom presets.

    Custom wins on key collision per the v1.1.4 spec.
    """
    merged = {k: dict(v) for k, v in BUILTIN_PRESETS.items()}
    custom = load_custom(custom_path, fs=fs) if custom_path else {}
    for pid, p in custom.items():
        merged[pid] = dict(p)
    return merged


# ---------------------------------------------------------------------
# export_submission / save_submission
# ---------------------------------------------------------------------

SUBMISSION_SCHEMA_VERSION = 1


def export_submission(preset_id, ip=None, quirks=None, contact=None, user_preset=None):
    """Build a JSON-ready submission dict for upstream contribution.

    `user_preset` is required for new presets (preset_id not in
    built-ins); for existing presets it is optional and overrides
    individual fields.
    """
    if not preset_id or not isinstance(preset_id, str):
        raise ValueError("preset_id is required")
    base = BUILTIN_PRESETS.get(preset_id)
    if base is None and not user_preset:
        raise ValueError("user_preset is required for new preset_id " + repr(preset_id))
    body = dict(base) if base else {}
    if user_preset:
        if not _validate_preset(user_preset):
            raise ValueError("user_preset failed schema validation")
        body.update(user_preset)
    return {
        "schema_version": SUBMISSION_SCHEMA_VERSION,
        "preset_id": preset_id,
        "preset": body,
        "device": {
            "ip": ip or "",
            "quirks": list(quirks or []),
        },
        "contact": contact or "",
    }


def _ts(now=None):
    # UTC keeps exported submission filenames deterministic across timezones.
    t = _time.gmtime(now() if callable(now) else (now if now else _time.time()))
    return _time.strftime("%Y%m%d-%H%M%S", t)


def save_submission(submission, root_dir, *, now=None, fs=None):
    """Write a submission to addon_data/preset-submission-<ts>.json.

    Returns the absolute path written.
    """
    if not isinstance(submission, dict):
        raise ValueError("submission must be a dict")
    fs = fs if fs is not None else _RealFS()
    pid = submission.get("preset_id", "preset")
    safe = _re.sub(r"[^A-Za-z0-9_.-]+", "_", str(pid))
    # Forward-slash join keeps addon-data paths portable across platforms.
    path = posixpath.join(root_dir, "preset-submission-" + safe + "-" + _ts(now) + ".json")
    fs.write(path, json.dumps(submission, sort_keys=True, indent=2))
    return path


# ---------------------------------------------------------------------
# compare_versions / firmware_warning
# ---------------------------------------------------------------------

_VERSION_RE = _re.compile(r"^[vV]?(\d+(?:\.\d+)*)")


def _parse_version(v):
    if not v:
        return None
    m = _VERSION_RE.match(str(v).strip())
    if not m:
        return None
    try:
        return tuple(int(x) for x in m.group(1).split("."))
    except Exception:
        return None


def compare_versions(a, b):
    """Return -1 if a<b, 0 if a==b, 1 if a>b, None on parse failure."""
    pa = _parse_version(a)
    pb = _parse_version(b)
    if pa is None or pb is None:
        return None
    # Pad to equal length
    L = max(len(pa), len(pb))
    pa = pa + (0,) * (L - len(pa))
    pb = pb + (0,) * (L - len(pb))
    return (pa > pb) - (pa < pb)


def firmware_warning(preset, device_firmware):
    """Return a warning string if the device firmware is older than
    the preset's firmware_min, else None.

    None when:
      - the preset has no firmware_min,
      - device_firmware is unknown / unparsable (we don't warn on
        ambiguity; that would be a false positive),
      - the device firmware is >= the minimum.
    """
    if not isinstance(preset, dict):
        return None
    minimum = preset.get("firmware_min")
    if not minimum:
        return None
    cmp = compare_versions(device_firmware, minimum)
    if cmp is None:
        return None
    if cmp < 0:
        return (
            "Device firmware "
            + str(device_firmware)
            + " is older than the preset minimum "
            + str(minimum)
            + ". Some commands may not work."
        )
    return None
