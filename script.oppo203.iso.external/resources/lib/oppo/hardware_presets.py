"""Hardware presets and device-specific quirks (v1.0.5).

Each preset is a dict describing how this add-on should talk to a given
player family. Consumers (wizard, oppo_control, service) call
`get_preset(key)` to retrieve a preset, and `select_power_command(key)` /
`select_play_command(key)` for the right commands to send.

Adding a new preset = add an entry to PRESETS with safe defaults.
"""

from __future__ import annotations

from typing import cast

# Canonical preset keys (kept in a list so order is stable for UI).
PRESET_KEYS: list[str] = [
    "udp_203",
    "udp_205",
    "udp_203_jailbroken",
    "udp_205_jailbroken",
    "chinoppo",
    "chinoppo_m9702",
    "chinoppo_m9201",
    "chinoppo_m9203",
    "chinoppo_m9205c",
    "reavon_ubrx100",
    "reavon_ubrx110",
    "reavon_ubrx200",
    "magnetar_udp800",
    "magnetar_udp900",
    "zappiti_reference",
    "generic_oppo_clone",
]


def _base() -> dict[str, object]:
    return {
        "label": "Generic",
        "family": "oppo",
        "control_port": 23,
        "supports_http": True,
        "supports_ip_control": True,
        "power_on": "#PON",
        "power_off": "#POF",
        "play": "#PLA",
        "pause": "#PAU",
        "stop": "#STP",
        "eject": "#EJT",
        "query_power": "#QPW",
        "needs_eject_before_play": False,  # Chinoppo and friends
        "use_eject_for_power_on": False,  # Chinoppo: #EJT instead of #PON
        "supports_quick_start": True,
        "wol_recommended": True,
        "notes": "",
    }


PRESETS: dict[str, dict[str, object]] = {
    "udp_203": dict(
        _base(), label="OPPO UDP-203", notes="Reference OPPO UDP-203. Full IP-control support."
    ),
    "udp_205": dict(
        _base(), label="OPPO UDP-205", notes="Reference OPPO UDP-205. Full IP-control support."
    ),
    "udp_203_jailbroken": dict(
        _base(),
        label="OPPO UDP-203 (Jailbroken)",
        notes="Jailbroken firmware. Same IP-control protocol as stock; "
        "additional file-list endpoints may be exposed but are not used "
        "by default for safety.",
    ),
    "udp_205_jailbroken": dict(
        _base(),
        label="OPPO UDP-205 (Jailbroken)",
        notes="Jailbroken firmware. Same IP-control protocol as stock.",
    ),
    "chinoppo": dict(
        _base(),
        label="Chinoppo (generic clone)",
        family="chinoppo",
        supports_http=False,
        needs_eject_before_play=True,
        use_eject_for_power_on=True,
        notes="Generic Chinese OPPO clone. Use #EJT to wake from standby; "
        "follow with #PLA after disc detection. HTTP not reliable.",
    ),
    "chinoppo_m9702": dict(
        _base(),
        label="Chinoppo M9702",
        family="chinoppo",
        supports_http=False,
        needs_eject_before_play=True,
        use_eject_for_power_on=True,
        notes="MeCool/Magnetar-derived M9702. Same protocol as generic Chinoppo.",
    ),
    "chinoppo_m9201": dict(
        _base(),
        label="Chinoppo M9201",
        family="chinoppo",
        supports_http=False,
        needs_eject_before_play=True,
        use_eject_for_power_on=True,
        notes="M9201. Older firmware; longer settle time may be needed.",
    ),
    "chinoppo_m9203": dict(
        _base(),
        label="Chinoppo M9203",
        family="chinoppo",
        supports_http=False,
        needs_eject_before_play=True,
        use_eject_for_power_on=True,
        notes="M9203.",
    ),
    "chinoppo_m9205c": dict(
        _base(),
        label="Chinoppo M9205C",
        family="chinoppo",
        supports_http=False,
        needs_eject_before_play=True,
        use_eject_for_power_on=True,
        notes="M9205C. Like M9203 with revised AV board.",
    ),
    "reavon_ubrx100": dict(
        _base(),
        label="Reavon UBR-X100",
        family="reavon",
        supports_http=False,
        notes="Reavon UBR-X100. IP-control protocol mirrors OPPO UDP-203 with "
        "minor differences; stock #PON/#POF/#PLA/#STP work.",
    ),
    "reavon_ubrx110": dict(
        _base(),
        label="Reavon UBR-X110",
        family="reavon",
        supports_http=False,
        notes="Reavon UBR-X110.",
    ),
    "reavon_ubrx200": dict(
        _base(),
        label="Reavon UBR-X200",
        family="reavon",
        supports_http=False,
        notes="Reavon UBR-X200 (4K UHD). Slower boot; recommend 8s power-on delay.",
    ),
    "magnetar_udp800": dict(
        _base(),
        label="Magnetar UDP800",
        family="magnetar",
        supports_http=False,
        notes="Magnetar UDP800. Compatible with OPPO IP-control set.",
    ),
    "magnetar_udp900": dict(
        _base(),
        label="Magnetar UDP900",
        family="magnetar",
        supports_http=False,
        notes="Magnetar UDP900.",
    ),
    "zappiti_reference": dict(
        _base(),
        label="Zappiti Reference",
        family="zappiti",
        control_port=23,
        supports_http=True,
        supports_quick_start=False,
        notes="Zappiti Reference. Different control flow; only the OPPO-style "
        "IP-control subset is used here. Quick Start not applicable.",
    ),
    "generic_oppo_clone": dict(
        _base(),
        label="Generic OPPO clone",
        family="generic",
        supports_http=False,
        notes="Catch-all for unknown OPPO-protocol clones.",
    ),
}


def get_preset(key: object) -> dict[str, object]:
    """Return a preset dict (or generic_oppo_clone fallback)."""
    if not key:
        return PRESETS["generic_oppo_clone"]
    return PRESETS.get(str(key).lower(), PRESETS["generic_oppo_clone"])


def list_presets() -> list[tuple[str, object]]:
    """Return [(key, label), ...] for UI selection."""
    return [(k, PRESETS[k]["label"]) for k in PRESET_KEYS]


def select_power_on_command(key: object) -> str:
    """Return the power-on command for a given preset.

    Chinoppo-class devices use #EJT (no #PON wake support).
    """
    p = get_preset(key)
    return cast(str, p["eject"] if p.get("use_eject_for_power_on") else p["power_on"])


def select_play_command(key: object) -> list[str]:
    """Return either ['#PLA'] or ['#EJT', '#PLA'] depending on quirks."""
    p = get_preset(key)
    if p.get("needs_eject_before_play"):
        return [cast(str, p["eject"]), cast(str, p["play"])]
    return [cast(str, p["play"])]


def select_recommended_power_delay(key: object) -> int:
    """Return a sensible power-on settle time (seconds) per preset."""
    p = get_preset(key)
    if p.get("family") == "reavon" and key == "reavon_ubrx200":
        return 8
    if p.get("family") == "chinoppo":
        return 6
    return 5


def supports_http(key: object) -> bool:
    return bool(get_preset(key).get("supports_http"))


def is_chinoppo_family(key: object) -> bool:
    return get_preset(key).get("family") == "chinoppo"
