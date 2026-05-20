"""Deterministic Kodi-to-player path mapping helpers.

v2.5.2 Build 3 adds this pure helper for the OPPO/Chinoppo NAS playback
roadmap.  It intentionally performs no hardware control and no playback launch;
it only translates a Kodi-visible path into the path expected inside a player
that has mounted the same NAS media tree through AutoScript/NFS.
"""
from __future__ import annotations

from dataclasses import dataclass
import posixpath
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit


DEFAULT_RULE_SEPARATOR = "=>"


class PathMappingError(ValueError):
    """Base error for invalid path-mapping configuration."""


class InvalidPathMappingRule(PathMappingError):
    """Raised when a mapping rule is missing a usable prefix."""


class NoMatchingPathRule(PathMappingError):
    """Raised by strict callers when no mapping rule matches the Kodi path."""


@dataclass(frozen=True)
class PathMappingRule:
    """A deterministic prefix replacement rule.

    ``kodi_prefix`` is the path namespace Kodi sees, for example
    ``smb://truenas/media/``.  ``player_prefix`` is the namespace the
    OPPO/Chinoppo player sees after the NAS has been mounted, for example
    ``/mnt/nas/media/``.
    """

    kodi_prefix: str
    player_prefix: str
    label: str = ""
    case_sensitive: bool = False
    decode_url: bool = True

    def __post_init__(self) -> None:
        if not str(self.kodi_prefix).strip():
            raise InvalidPathMappingRule("kodi_prefix is required")
        if not str(self.player_prefix).strip():
            raise InvalidPathMappingRule("player_prefix is required")


def _coerce_rule(rule: PathMappingRule | dict[str, Any]) -> PathMappingRule:
    if isinstance(rule, PathMappingRule):
        return rule
    if isinstance(rule, dict):
        return PathMappingRule(
            kodi_prefix=str(rule.get("kodi_prefix", "")),
            player_prefix=str(rule.get("player_prefix", "")),
            label=str(rule.get("label", "")),
            case_sensitive=bool(rule.get("case_sensitive", False)),
            decode_url=bool(rule.get("decode_url", True)),
        )
    raise InvalidPathMappingRule(f"unsupported rule type: {type(rule).__name__}")


def _collapse_posix_path(path: str) -> str:
    """Normalize repeated separators in a POSIX-like path without losing root."""
    if path in ("", "/"):
        return path
    trailing = path.endswith("/")
    normalized = posixpath.normpath(path)
    if normalized == ".":
        normalized = ""
    if trailing and normalized and not normalized.endswith("/"):
        normalized += "/"
    return normalized


def normalize_kodi_path(path: str, *, decode_url: bool = True) -> str:
    """Return a stable representation of a Kodi-visible path.

    SMB and other URL-like paths keep their URI form while URL-encoded suffixes
    are decoded by default. Local filesystem paths are normalized with POSIX
    separators because the player-side mount namespace is Linux-like.
    """
    text = "" if path is None else str(path).strip()
    if decode_url:
        text = unquote(text)
    text = text.replace("\\", "/")
    parsed = urlsplit(text)
    if parsed.scheme and parsed.netloc:
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc
        normalized_path = _collapse_posix_path(parsed.path or "/")
        if parsed.query:
            normalized_path = f"{normalized_path}?{parsed.query}"
        if parsed.fragment:
            normalized_path = f"{normalized_path}#{parsed.fragment}"
        return f"{scheme}://{netloc}{normalized_path}"
    return _collapse_posix_path(text)


def normalize_player_path(path: str) -> str:
    """Return a Linux/player-side path with POSIX separators."""
    return _collapse_posix_path(str(path or "").strip().replace("\\", "/"))


def _match_text(text: str, case_sensitive: bool) -> str:
    return text if case_sensitive else text.lower()


def _has_prefix_boundary(path: str, prefix: str) -> bool:
    """Avoid accidental matches such as /media2 matching /media."""
    if len(path) == len(prefix):
        return True
    if prefix.endswith(("/", "://")):
        return True
    return path[len(prefix):len(prefix) + 1] in {"/", ""}


def _relative_suffix(path: str, prefix: str, *, case_sensitive: bool) -> str | None:
    comparable_path = _match_text(path, case_sensitive)
    comparable_prefix = _match_text(prefix, case_sensitive)
    if not comparable_path.startswith(comparable_prefix):
        return None
    if not _has_prefix_boundary(comparable_path, comparable_prefix):
        return None
    suffix = path[len(prefix):]
    return suffix.lstrip("/")


def _join_player_prefix(prefix: str, suffix: str) -> str:
    normalized_prefix = normalize_player_path(prefix)
    suffix = normalize_player_path(suffix).lstrip("/")
    if not suffix:
        return normalized_prefix
    if normalized_prefix.endswith("/"):
        return normalized_prefix + suffix
    return normalized_prefix + "/" + suffix


def map_kodi_path_to_player_path(
    kodi_path: str,
    rules: Iterable[PathMappingRule | dict[str, Any]],
    *,
    strict: bool = False,
) -> str | None:
    """Map a Kodi-visible media path to a player-mounted NAS path.

    Returns ``None`` when no rule matches unless ``strict`` is true, in which
    case ``NoMatchingPathRule`` is raised. The first matching rule wins so users
    can put more specific mappings before broad fallbacks.
    """
    detail = explain_path_mapping(kodi_path, rules)
    if detail["matched"]:
        return str(detail["player_path"])
    if strict:
        raise NoMatchingPathRule(str(detail["reason"]))
    return None


def explain_path_mapping(
    kodi_path: str,
    rules: Iterable[PathMappingRule | dict[str, Any]],
) -> dict[str, Any]:
    """Return dry-run diagnostics for a Kodi-to-player path mapping attempt."""
    candidate_rules = [_coerce_rule(rule) for rule in rules]
    raw_kodi_path = "" if kodi_path is None else str(kodi_path)
    if not raw_kodi_path.strip():
        return {
            "matched": False,
            "reason": "empty_kodi_path",
            "kodi_path": raw_kodi_path,
            "normalized_kodi_path": "",
            "player_path": None,
            "rule": None,
            "rule_count": len(candidate_rules),
        }
    for index, rule in enumerate(candidate_rules):
        normalized_path = normalize_kodi_path(raw_kodi_path, decode_url=rule.decode_url)
        normalized_prefix = normalize_kodi_path(rule.kodi_prefix, decode_url=rule.decode_url)
        suffix = _relative_suffix(normalized_path, normalized_prefix, case_sensitive=rule.case_sensitive)
        if suffix is None:
            continue
        player_path = _join_player_prefix(rule.player_prefix, suffix)
        return {
            "matched": True,
            "reason": "matched",
            "kodi_path": raw_kodi_path,
            "normalized_kodi_path": normalized_path,
            "player_path": player_path,
            "suffix": suffix,
            "rule": {
                "index": index,
                "label": rule.label,
                "kodi_prefix": rule.kodi_prefix,
                "player_prefix": rule.player_prefix,
                "case_sensitive": rule.case_sensitive,
                "decode_url": rule.decode_url,
            },
            "rule_count": len(candidate_rules),
        }
    return {
        "matched": False,
        "reason": "no_matching_rule",
        "kodi_path": raw_kodi_path,
        "normalized_kodi_path": normalize_kodi_path(raw_kodi_path),
        "player_path": None,
        "rule": None,
        "rule_count": len(candidate_rules),
    }


def parse_mapping_rule(line: str, *, separator: str = DEFAULT_RULE_SEPARATOR) -> PathMappingRule:
    """Parse one text rule in the form ``kodi_prefix => player_prefix``."""
    text = "" if line is None else str(line).strip()
    if not text or text.startswith("#"):
        raise InvalidPathMappingRule("mapping rule is blank or commented")
    if separator not in text:
        raise InvalidPathMappingRule(f"mapping rule must contain {separator!r}")
    left, right = text.split(separator, 1)
    return PathMappingRule(left.strip(), right.strip())


def parse_mapping_rules(text: str, *, separator: str = DEFAULT_RULE_SEPARATOR) -> list[PathMappingRule]:
    """Parse newline-separated path-mapping rules, ignoring blank/comments."""
    rules: list[PathMappingRule] = []
    for line in str(text or "").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        rules.append(parse_mapping_rule(stripped, separator=separator))
    return rules


def rules_from_settings(settings: Any) -> list[PathMappingRule]:
    """Create mapping rules from Settings/dict-like values when configured.

    Build 3 remains a helper-only slice, but this adapter lets later wizard and
    playback builds reuse the same deterministic rule parsing without changing
    this module's public contract.
    """
    getter = settings.get if hasattr(settings, "get") else dict(settings).get
    text_rules = getter("nas_path_mapping_rules", "") or ""
    parsed = parse_mapping_rules(text_rules)
    kodi_prefix = str(getter("nas_kodi_path_prefix", "") or "").strip()
    player_prefix = str(getter("nas_player_path_prefix", "") or "").strip()
    if kodi_prefix or player_prefix:
        parsed.append(PathMappingRule(kodi_prefix, player_prefix, label="settings_prefix"))
    return parsed

