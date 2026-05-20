"""Validated OPPO remote command-map loader.

v2.9.1 Build 3 moves the canonical 76-key OPPO command map out of
``settings_reader.DEFAULTS`` and into ``resources/data/oppo_command_map.json``.
This module keeps runtime callers dependency-free while validating the protected
command-map invariants before the data is used.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

try:  # package import
    from .constants import OPPO_COMMAND_MAP_SIZE
except ImportError:  # top-level/audit import compatibility
    from constants import OPPO_COMMAND_MAP_SIZE  # type: ignore

FORBIDDEN_COMMAND_TOKENS: tuple[str, ...] = ("#SIS", "#PGU", "#PGD")
DEFAULT_COMMAND_MAP_PATH = Path(__file__).resolve().parents[1] / "data" / "oppo_command_map.json"


@dataclass(frozen=True)
class CommandMap:
    """Immutable validated OPPO command-map wrapper."""

    entries: Mapping[str, str]

    def __post_init__(self) -> None:
        normalized = dict(self.entries)
        if len(normalized) != OPPO_COMMAND_MAP_SIZE:
            raise ValueError(
                f"OPPO command map must contain {OPPO_COMMAND_MAP_SIZE} keys; "
                f"found {len(normalized)}"
            )
        non_string = [key for key, value in normalized.items() if not isinstance(key, str) or not isinstance(value, str)]
        if non_string:
            raise TypeError("OPPO command map keys and values must be strings")
        offenders = sorted({token for value in normalized.values() for token in FORBIDDEN_COMMAND_TOKENS if token in value})
        if offenders:
            raise ValueError("Forbidden OPPO command tokens found: " + ", ".join(offenders))
        object.__setattr__(self, "entries", MappingProxyType(normalized))

    def as_dict(self) -> dict[str, str]:
        """Return a mutable copy for compatibility with existing callers."""
        return dict(self.entries)

    def as_json(self) -> str:
        """Return compact deterministic JSON for legacy settings defaults."""
        return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))


def load_command_map(path: str | Path | None = None) -> CommandMap:
    """Load and validate a command map from JSON."""
    source = Path(path) if path is not None else DEFAULT_COMMAND_MAP_PATH
    raw = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("OPPO command-map JSON must contain an object")
    return CommandMap(raw)


def load_default_command_map() -> dict[str, str]:
    """Return the canonical OPPO command map as a mutable compatibility dict."""
    return load_command_map().as_dict()


def load_default_command_map_json() -> str:
    """Return the canonical command map as compact JSON for settings defaults."""
    return load_command_map().as_json()
