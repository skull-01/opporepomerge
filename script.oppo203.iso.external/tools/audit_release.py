#!/usr/bin/env python3
"""Release audit helper for script.oppo203.iso.external.

This tool is intentionally dependency-free so a local AI, CI job, or user can
run the same core release checks after unpacking a build artifact.
"""

from __future__ import annotations

import argparse
import compileall
import json
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

FORBIDDEN_COMMAND_TOKENS = ("#SIS", "#PGU", "#PGD")
DEFAULT_EXPECTED_COMMAND_MAP_KEYS = 76
DEFAULT_MIN_COVERAGE_PERCENT = 99


class AuditCheck:
    """Typed release-audit result used by reporter implementations.

    This is intentionally a small dependency-free value object instead of a
    dataclass because several legacy tests load this tool with
    ``importlib.util.module_from_spec`` without first registering the module in
    ``sys.modules``. That import style is incompatible with dataclasses on some
    Python versions, while this explicit class preserves the same semantics.
    """

    __slots__ = ("name", "status", "detail")

    def __init__(self, name: str, status: str, detail: str = "ok") -> None:
        self.name = name
        self.status = status
        self.detail = detail

    @property
    def passed(self) -> bool:
        return self.status == "ok"

    def as_dict(self) -> dict[str, str]:
        return {"name": self.name, "status": self.status, "detail": self.detail}

    @classmethod
    def from_mapping(cls, item: dict[str, str]) -> AuditCheck:
        return cls(
            name=str(item.get("name", "unknown")),
            status=str(item.get("status", "fail")),
            detail=str(item.get("detail", "")),
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, AuditCheck) and self.as_dict() == other.as_dict()

    def __repr__(self) -> str:
        return f"AuditCheck(name={self.name!r}, status={self.status!r}, detail={self.detail!r})"


class TextReporter:
    """Render audit checks using the historical text CLI format."""

    def render(self, root: Path, checks: list[AuditCheck]) -> str:
        failed = [item for item in checks if not item.passed]
        lines = []
        for item in checks:
            prefix = "OK" if item.passed else "FAIL"
            lines.append(f"{prefix}: {item.name} - {item.detail}")
        lines.append(
            f"SUMMARY: {'PASS' if not failed else 'FAIL'} ({len(checks) - len(failed)}/{len(checks)} checks passed)"
        )
        return "\n".join(lines)


class JsonReporter:
    """Render audit checks as JSON while preserving the legacy schema."""

    def render(self, root: Path, checks: list[AuditCheck]) -> str:
        failed = [item for item in checks if not item.passed]
        payload = {
            "root": str(root),
            "ok": not failed,
            "results": [item.as_dict() for item in checks],
        }
        return json.dumps(payload, indent=2, sort_keys=True)


def project_root(start: Path | None = None) -> Path:
    if start is None:
        start = Path.cwd()
    start = start.resolve()
    for candidate in (start, *start.parents):
        if (candidate / "addon.xml").exists() and (
            candidate / "resources" / "settings.xml"
        ).exists():
            return candidate
    raise RuntimeError(
        "Could not find project root containing addon.xml and resources/settings.xml"
    )


def ok(name: str, detail: str = "ok") -> dict[str, str]:
    return {"name": name, "status": "ok", "detail": detail}


def fail(name: str, detail: str) -> dict[str, str]:
    return {"name": name, "status": "fail", "detail": detail}


def audit_compile(root: Path) -> dict[str, str]:
    # Validate that all *project* sources byte-compile. Skip the local virtualenv
    # and build/VCS dirs (not our code), and direct throwaway bytecode to a private
    # temp dir so concurrent runs (e.g. pytest-xdist) do not race on shared
    # __pycache__ files (Windows .pyc rename collisions, WinError 5).
    skip_rx = re.compile(
        r"[\\/](?:\.venv|venv|env|build|dist|output|\.git|\.pytest_cache|"
        r"__pycache__|node_modules)(?:[\\/]|$)"
    )
    prev_prefix = sys.pycache_prefix
    pyc_tmp = tempfile.mkdtemp(prefix="audit_pyc_")
    sys.pycache_prefix = pyc_tmp
    try:
        passed = compileall.compile_dir(str(root), quiet=1, force=True, rx=skip_rx)
    finally:
        sys.pycache_prefix = prev_prefix
        shutil.rmtree(pyc_tmp, ignore_errors=True)
    return (
        ok("python_compile", "compileall passed")
        if passed
        else fail("python_compile", "compileall reported at least one failure")
    )


def audit_xml(root: Path) -> list[dict[str, str]]:
    results = []
    for rel in ("addon.xml", "resources/settings.xml"):
        try:
            ET.parse(root / rel)
            results.append(ok(f"xml:{rel}", "parsed"))
        except Exception as exc:  # pragma: no cover - failure path exercised by CLI users
            results.append(fail(f"xml:{rel}", str(exc)))
    return results


def _po_entries(po_text: str, token: str) -> list[str]:
    pattern = re.compile(rf'^\s*{re.escape(token)}\s+"(.*)"\s*$', re.MULTILINE)
    return pattern.findall(po_text)


def audit_locales(root: Path) -> list[dict[str, str]]:
    lang_root = root / "resources" / "language"
    files = sorted(lang_root.glob("resource.language.*/strings.po"))
    if not files:
        return [fail("locale_parity", "no strings.po files found")]

    result = []
    baseline_ids: set[str] | None = None
    baseline_name = ""
    for file in files:
        text = file.read_text(encoding="utf-8")
        msgctxt = _po_entries(text, "msgctxt")
        msgid = _po_entries(text, "msgid")
        msgstr = _po_entries(text, "msgstr")
        name = file.parent.name
        if not (len(msgctxt) == len(msgid) == len(msgstr)):
            result.append(
                fail(
                    f"locale:{name}",
                    f"unbalanced counts msgctxt={len(msgctxt)} msgid={len(msgid)} msgstr={len(msgstr)}",
                )
            )
            continue
        ids = set(msgctxt)
        if len(ids) != len(msgctxt):
            result.append(fail(f"locale:{name}", "duplicate msgctxt id found"))
            continue
        if baseline_ids is None:
            baseline_ids = ids
            baseline_name = name
            result.append(ok(f"locale:{name}", f"{len(ids)} msgctxt ids"))
            continue
        if ids != baseline_ids:
            missing = sorted(baseline_ids - ids)[:10]
            extra = sorted(ids - baseline_ids)[:10]
            result.append(
                fail(
                    f"locale:{name}",
                    f"msgctxt set differs from {baseline_name}; missing={missing} extra={extra}",
                )
            )
        else:
            result.append(ok(f"locale:{name}", f"{len(ids)} msgctxt ids"))
    return result


def audit_settings_strings(root: Path) -> dict[str, str]:
    settings_xml = root / "resources" / "settings.xml"
    en_po = root / "resources" / "language" / "resource.language.en_gb" / "strings.po"
    settings_text = settings_xml.read_text(encoding="utf-8")
    string_text = en_po.read_text(encoding="utf-8")
    used = set(re.findall(r'\b(?:label|help)="(\d+)"', settings_text))
    defined = {item.lstrip("#") for item in _po_entries(string_text, "msgctxt")}
    missing = sorted(used - defined)
    if missing:
        return fail("settings_string_ids", "missing string ids: " + ", ".join(missing[:20]))
    return ok("settings_string_ids", f"{len(used)} label/help ids covered")


def _import_settings_reader(root: Path):
    lib = root / "resources" / "lib"
    for path in (str(root), str(lib)):
        if path not in sys.path:
            sys.path.insert(0, path)
    try:
        from resources.lib.kodi import settings_reader  # type: ignore
    except Exception:  # pragma: no cover - legacy flat-layout fallback
        import settings_reader  # type: ignore
    return settings_reader


def _import_command_map(root: Path):
    lib = root / "resources" / "lib"
    for path in (str(root), str(lib)):
        if path not in sys.path:
            sys.path.insert(0, path)
    try:
        from resources.lib.oppo import command_map  # type: ignore
    except Exception:  # pragma: no cover - legacy flat-layout fallback
        import command_map  # type: ignore
    return command_map


def _import_constants(root: Path):
    lib = root / "resources" / "lib"
    for path in (str(root), str(lib)):
        if path not in sys.path:
            sys.path.insert(0, path)
    try:
        from resources.lib.oppo import constants  # type: ignore

        return constants
    except Exception:  # pragma: no cover - defensive fallback for legacy unpacked trees

        class LegacyConstants:
            OPPO_COMMAND_MAP_SIZE = DEFAULT_EXPECTED_COMMAND_MAP_KEYS
            MIN_COVERAGE_PERCENT = DEFAULT_MIN_COVERAGE_PERCENT

        return LegacyConstants


def _import_version(root: Path):
    lib = root / "resources" / "lib"
    for path in (str(root), str(lib)):
        if path not in sys.path:
            sys.path.insert(0, path)
    try:
        from resources.lib.kodi import version as version_module  # type: ignore
    except Exception:
        import version as version_module  # type: ignore
    return version_module


def audit_version_source(root: Path, expected_version: str | None = None) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    try:
        version_module = _import_version(root)
        source_version = str(version_module.ADDON_VERSION)
        build_id = str(getattr(version_module, "BUILD_ID", ""))
    except Exception as exc:
        return [fail("version_source", f"could not import resources.lib.version: {exc}")]
    results.append(ok("version_source", f"ADDON_VERSION={source_version}; BUILD_ID={build_id}"))
    try:
        addon_version = ET.parse(root / "addon.xml").getroot().attrib.get("version")
    except Exception as exc:
        results.append(fail("version_consistency", f"could not parse addon.xml: {exc}"))
        return results
    if addon_version != source_version:
        results.append(
            fail(
                "version_consistency",
                f"addon.xml version={addon_version}; version.py ADDON_VERSION={source_version}",
            )
        )
    elif expected_version is not None and source_version != expected_version:
        results.append(
            fail(
                "version_consistency",
                f"version.py ADDON_VERSION={source_version}; expected {expected_version}",
            )
        )
    else:
        detail = f"addon.xml and version.py agree on {source_version}"
        if expected_version is not None:
            detail += f"; expected-version={expected_version}"
        results.append(ok("version_consistency", detail))
    return results


def audit_command_map(root: Path) -> dict[str, str]:
    command_map_module = _import_command_map(root)
    try:
        command_map = command_map_module.load_default_command_map()
    except Exception as exc:
        return fail("command_map", f"default command-map load failed: {exc}")
    keys = list(command_map)
    values = list(command_map.values())
    expected_size = _import_constants(root).OPPO_COMMAND_MAP_SIZE
    if len(keys) != expected_size:
        return fail("command_map", f"expected {expected_size} keys, found {len(keys)}")
    if len(keys) != len(set(keys)):
        return fail("command_map", "duplicate keys found")
    offenders = [
        token for token in FORBIDDEN_COMMAND_TOKENS if any(token in value for value in values)
    ]
    if offenders:
        return fail("command_map", "forbidden command tokens found: " + ", ".join(offenders))
    return ok("command_map", f"{len(keys)} canonical keys; no forbidden tokens")


def audit_hardware_count(root: Path) -> dict[str, str]:
    sr = _import_settings_reader(root)
    settings_text = (root / "resources" / "settings.xml").read_text(encoding="utf-8")
    match = re.search(r'id="oppo_hardware_model"[^>]*values="([^"]+)"', settings_text)
    if not match:
        return fail("hardware_model_count", "oppo_hardware_model enum not found")
    enum_values = [item for item in match.group(1).split("|") if item]
    compat_count = len(sr.HARDWARE_COMPAT)
    if len(enum_values) != compat_count:
        return fail(
            "hardware_model_count",
            f"settings enum={len(enum_values)} HARDWARE_COMPAT={compat_count}",
        )
    return ok(
        "hardware_model_count",
        f"settings enum and HARDWARE_COMPAT both have {compat_count} entries",
    )


def audit_coverage_gate(root: Path) -> dict[str, str]:
    text = (root / ".coveragerc").read_text(encoding="utf-8")
    match = re.search(r"^fail_under\s*=\s*(\d+)\s*$", text, flags=re.MULTILINE)
    if not match:
        return fail("coverage_gate", "fail_under not found in .coveragerc")
    gate = int(match.group(1))
    min_gate = _import_constants(root).MIN_COVERAGE_PERCENT
    if gate < min_gate:
        return fail("coverage_gate", f"fail_under={gate}; expected at least {min_gate}")
    return ok("coverage_gate", f"fail_under={gate}")


RELEASE_EVIDENCE_ROOT = "release-evidence"
ARCHIVED_RELEASE_DOC_DIRS = (
    "docs/release-history",
    "docs/ai-handoff",
)


def resolve_release_artifact(root: Path, rel: str | Path) -> Path | None:
    """Return the current path for a release/audit artifact.

    GitHub Readiness Build G1 moved historical root Markdown artifacts into
    documentation archive folders to make the public repository root easier to
    maintain.  Legacy audit entries intentionally remain stable so older tests
    and evidence manifests can still ask for the original filename while this
    resolver finds the preserved archived copy.
    """
    rel_path = Path(rel)
    direct = root / rel_path
    if direct.exists():
        return direct
    if len(rel_path.parts) == 1 and rel_path.suffix.lower() == ".md":
        for directory in ARCHIVED_RELEASE_DOC_DIRS:
            candidate = root / directory / rel_path.name
            if candidate.exists():
                return candidate
    return None


def legacy_required_release_files() -> list[str]:
    return [
        ".coveragerc",
        "README.md",
        "reference.md",
        "web-references.md",
        "HARDWARE_VALIDATION_v2.0.0_BUILD4.md",
        "MVP_COMPLIANCE_MATRIX_v2.0.0_BUILD4.md",
        "RELEASE_NOTES_v2.0.0.md",
        "RELEASE_MANIFEST_v2.0.0.md",
        "MVP_COMPLIANCE_MATRIX_v2.0.0.md",
        "HARDWARE_VALIDATION_v2.0.0.md",
        "BUILD_NOTES_v2.0.0_BUILD6.md",
        "RELEASE_MANIFEST_v2.0.0_BUILD6.md",
        "BUILD_NOTES_v2.1.0_BUILD1.md",
        "RELEASE_MANIFEST_v2.1.0_BUILD1.md",
        "COVERAGE_REPORT_v2.1.0_BUILD1.md",
        "TEST_AUDIT_REPORT_v2.1.0_BUILD1.md",
        "BUILD_NOTES_v2.1.0_BUILD2.md",
        "RELEASE_MANIFEST_v2.1.0_BUILD2.md",
        "COVERAGE_REPORT_v2.1.0_BUILD2.md",
        "TEST_AUDIT_REPORT_v2.1.0_BUILD2.md",
        "BUILD_NOTES_v2.1.0_BUILD3.md",
        "RELEASE_MANIFEST_v2.1.0_BUILD3.md",
        "COVERAGE_REPORT_v2.1.0_BUILD3.md",
        "TEST_AUDIT_REPORT_v2.1.0_BUILD3.md",
        "BUILD_NOTES_v2.1.0_BUILD5.md",
        "RELEASE_MANIFEST_v2.1.0_BUILD5.md",
        "COVERAGE_REPORT_v2.1.0_BUILD5.md",
        "TEST_AUDIT_REPORT_v2.1.0_BUILD5.md",
        "BUILD_NOTES_v2.1.0_BUILD6.md",
        "RELEASE_MANIFEST_v2.1.0_BUILD6.md",
        "COVERAGE_REPORT_v2.1.0_BUILD6.md",
        "TEST_AUDIT_REPORT_v2.1.0_BUILD6.md",
        "BUILD_NOTES_v2.1.0_BUILD7.md",
        "RELEASE_MANIFEST_v2.1.0_BUILD7.md",
        "COVERAGE_REPORT_v2.1.0_BUILD7.md",
        "TEST_AUDIT_REPORT_v2.1.0_BUILD7.md",
        "BUILD_NOTES_v2.1.0_BUILD8.md",
        "RELEASE_MANIFEST_v2.1.0_BUILD8.md",
        "COVERAGE_REPORT_v2.1.0_BUILD8.md",
        "TEST_AUDIT_REPORT_v2.1.0_BUILD8.md",
        "BUILD_NOTES_v2.2.0_BUILD1.md",
        "RELEASE_MANIFEST_v2.2.0_BUILD1.md",
        "COVERAGE_REPORT_v2.2.0_BUILD1.md",
        "TEST_AUDIT_REPORT_v2.2.0_BUILD1.md",
        "BUILD_NOTES_v2.2.0_BUILD2.md",
        "RELEASE_MANIFEST_v2.2.0_BUILD2.md",
        "COVERAGE_REPORT_v2.2.0_BUILD2.md",
        "TEST_AUDIT_REPORT_v2.2.0_BUILD2.md",
        "BUILD_NOTES_v2.2.0_BUILD3.md",
        "RELEASE_MANIFEST_v2.2.0_BUILD3.md",
        "COVERAGE_REPORT_v2.2.0_BUILD3.md",
        "TEST_AUDIT_REPORT_v2.2.0_BUILD3.md",
        "BUILD_NOTES_v2.2.0_BUILD4.md",
        "RELEASE_MANIFEST_v2.2.0_BUILD4.md",
        "COVERAGE_REPORT_v2.2.0_BUILD4.md",
        "TEST_AUDIT_REPORT_v2.2.0_BUILD4.md",
        "BUILD_NOTES_v2.2.0_BUILD5.md",
        "RELEASE_MANIFEST_v2.2.0_BUILD5.md",
        "COVERAGE_REPORT_v2.2.0_BUILD5.md",
        "TEST_AUDIT_REPORT_v2.2.0_BUILD5.md",
        "BUILD_NOTES_v2.2.0_BUILD6.md",
        "RELEASE_MANIFEST_v2.2.0_BUILD6.md",
        "COVERAGE_REPORT_v2.2.0_BUILD6.md",
        "TEST_AUDIT_REPORT_v2.2.0_BUILD6.md",
        "BUILD_NOTES_v2.2.0_BUILD7.md",
        "RELEASE_MANIFEST_v2.2.0_BUILD7.md",
        "COVERAGE_REPORT_v2.2.0_BUILD7.md",
        "TEST_AUDIT_REPORT_v2.2.0_BUILD7.md",
        "BUILD_NOTES_v2.2.0_BUILD8.md",
        "RELEASE_MANIFEST_v2.2.0_BUILD8.md",
        "COVERAGE_REPORT_v2.2.0_BUILD8.md",
        "TEST_AUDIT_REPORT_v2.2.0_BUILD8.md",
        "MERGE_PARITY_AUDIT_v2.2.0_BUILD8.md",
        "BUILD_NOTES_v2.2.0_BUILD9.md",
        "RELEASE_MANIFEST_v2.2.0_BUILD9.md",
        "COVERAGE_REPORT_v2.2.0_BUILD9.md",
        "TEST_AUDIT_REPORT_v2.2.0_BUILD9.md",
        "MERGE_PARITY_AUDIT_v2.2.0_BUILD9.md",
        "BUILD_NOTES_v2.2.0_BUILD10.md",
        "RELEASE_MANIFEST_v2.2.0_BUILD10.md",
        "COVERAGE_REPORT_v2.2.0_BUILD10.md",
        "TEST_AUDIT_REPORT_v2.2.0_BUILD10.md",
        "MERGE_COMPLIANCE_MATRIX_v2.2.0_BUILD10.md",
        "BUILD_NOTES_v2.2.0_BUILD11.md",
        "RELEASE_MANIFEST_v2.2.0_BUILD11.md",
        "COVERAGE_REPORT_v2.2.0_BUILD11.md",
        "TEST_AUDIT_REPORT_v2.2.0_BUILD11.md",
        "MERGE_COMPLIANCE_MATRIX_v2.2.0_BUILD11.md",
        "BUILD_NOTES_v2.2.0_RELEASE.md",
        "RELEASE_MANIFEST_v2.2.0_RELEASE.md",
        "COVERAGE_REPORT_v2.2.0_RELEASE.md",
        "TEST_AUDIT_REPORT_v2.2.0_RELEASE.md",
        "MERGE_COMPLIANCE_MATRIX_v2.2.0_RELEASE.md",
        "RELEASE_NOTES_v2.2.0.md",
        "HARDWARE_VALIDATION_v2.2.0.md",
        "BUILD_NOTES_v2.5.0_BUILD1.md",
        "RELEASE_MANIFEST_v2.5.0_BUILD1.md",
        "COVERAGE_REPORT_v2.5.0_BUILD1.md",
        "TEST_AUDIT_REPORT_v2.5.0_BUILD1.md",
        "BUILD_NOTES_v2.5.0_BUILD2.md",
        "RELEASE_MANIFEST_v2.5.0_BUILD2.md",
        "COVERAGE_REPORT_v2.5.0_BUILD2.md",
        "TEST_AUDIT_REPORT_v2.5.0_BUILD2.md",
        "BUILD_NOTES_v2.5.0_BUILD3.md",
        "RELEASE_MANIFEST_v2.5.0_BUILD3.md",
        "COVERAGE_REPORT_v2.5.0_BUILD3.md",
        "TEST_AUDIT_REPORT_v2.5.0_BUILD3.md",
        "BUILD_NOTES_v2.5.0_BUILD4.md",
        "RELEASE_MANIFEST_v2.5.0_BUILD4.md",
        "COVERAGE_REPORT_v2.5.0_BUILD4.md",
        "TEST_AUDIT_REPORT_v2.5.0_BUILD4.md",
        "BUILD_NOTES_v2.5.0_BUILD5.md",
        "RELEASE_MANIFEST_v2.5.0_BUILD5.md",
        "COVERAGE_REPORT_v2.5.0_BUILD5.md",
        "TEST_AUDIT_REPORT_v2.5.0_BUILD5.md",
        "BUILD_NOTES_v2.5.0_BUILD6.md",
        "RELEASE_MANIFEST_v2.5.0_BUILD6.md",
        "COVERAGE_REPORT_v2.5.0_BUILD6.md",
        "TEST_AUDIT_REPORT_v2.5.0_BUILD6.md",
        "BUILD_NOTES_v2.5.0_BUILD7.md",
        "RELEASE_MANIFEST_v2.5.0_BUILD7.md",
        "COVERAGE_REPORT_v2.5.0_BUILD7.md",
        "TEST_AUDIT_REPORT_v2.5.0_BUILD7.md",
        "BUILD_NOTES_v2.5.0_FINAL.md",
        "RELEASE_MANIFEST_v2.5.0_FINAL.md",
        "RELEASE_NOTES_v2.5.0.md",
        "HARDWARE_VALIDATION_v2.5.0_FINAL.md",
        "COVERAGE_REPORT_v2.5.0_FINAL.md",
        "TEST_AUDIT_REPORT_v2.5.0_FINAL.md",
        "HARDWARE_VALIDATION_TRACKER_v2.5.0.md",
        "ROADMAP_v2.5.0.md",
        "BUILD_NOTES_v2.5.2_BUILD1.md",
        "RELEASE_MANIFEST_v2.5.2_BUILD1.md",
        "RELEASE_NOTES_v2.5.2_BUILD1.md",
        "HARDWARE_VALIDATION_TRACKER_v2.5.2.md",
        "COVERAGE_REPORT_v2.5.2_BUILD1.md",
        "TEST_AUDIT_REPORT_v2.5.2_BUILD1.md",
        "BUILD_NOTES_v2.5.2_BUILD2.md",
        "RELEASE_MANIFEST_v2.5.2_BUILD2.md",
        "RELEASE_NOTES_v2.5.2_BUILD2.md",
        "COVERAGE_REPORT_v2.5.2_BUILD2.md",
        "TEST_AUDIT_REPORT_v2.5.2_BUILD2.md",
        "BUILD_NOTES_v2.5.2_BUILD3.md",
        "RELEASE_MANIFEST_v2.5.2_BUILD3.md",
        "RELEASE_NOTES_v2.5.2_BUILD3.md",
        "COVERAGE_REPORT_v2.5.2_BUILD3.md",
        "TEST_AUDIT_REPORT_v2.5.2_BUILD3.md",
        "BUILD_NOTES_v2.5.2_BUILD4.md",
        "RELEASE_MANIFEST_v2.5.2_BUILD4.md",
        "RELEASE_NOTES_v2.5.2_BUILD4.md",
        "COVERAGE_REPORT_v2.5.2_BUILD4.md",
        "TEST_AUDIT_REPORT_v2.5.2_BUILD4.md",
        "BUILD_NOTES_v2.5.3_BUILD1.md",
        "RELEASE_MANIFEST_v2.5.3_BUILD1.md",
        "RELEASE_NOTES_v2.5.3_BUILD1.md",
        "COVERAGE_REPORT_v2.5.3_BUILD1.md",
        "TEST_AUDIT_REPORT_v2.5.3_BUILD1.md",
        "BUILD_NOTES_v2.5.3_BUILD2.md",
        "RELEASE_MANIFEST_v2.5.3_BUILD2.md",
        "RELEASE_NOTES_v2.5.3_BUILD2.md",
        "COVERAGE_REPORT_v2.5.3_BUILD2.md",
        "TEST_AUDIT_REPORT_v2.5.3_BUILD2.md",
        "HARDWARE_VALIDATION_v2.5.3_BUILD2.md",
        "BUILD_NOTES_v2.5.3_BUILD3.md",
        "RELEASE_MANIFEST_v2.5.3_BUILD3.md",
        "RELEASE_NOTES_v2.5.3_BUILD3.md",
        "COVERAGE_REPORT_v2.5.3_BUILD3.md",
        "TEST_AUDIT_REPORT_v2.5.3_BUILD3.md",
        "HARDWARE_VALIDATION_v2.5.3_BUILD3.md",
        "BUILD_NOTES_v2.5.3_BUILD4.md",
        "RELEASE_MANIFEST_v2.5.3_BUILD4.md",
        "RELEASE_NOTES_v2.5.3_BUILD4.md",
        "COVERAGE_REPORT_v2.5.3_BUILD4.md",
        "TEST_AUDIT_REPORT_v2.5.3_BUILD4.md",
        "HARDWARE_VALIDATION_v2.5.3_BUILD4.md",
        "BUILD_NOTES_v2.5.3_BUILD5.md",
        "RELEASE_MANIFEST_v2.5.3_BUILD5.md",
        "RELEASE_NOTES_v2.5.3_BUILD5.md",
        "COVERAGE_REPORT_v2.5.3_BUILD5.md",
        "TEST_AUDIT_REPORT_v2.5.3_BUILD5.md",
        "HARDWARE_VALIDATION_v2.5.3_BUILD5.md",
        "HARDWARE_VALIDATION_READINESS_v2.5.3_BUILD5.md",
        "BUILD_NOTES_v2.5.3_BUILD6.md",
        "RELEASE_MANIFEST_v2.5.3_BUILD6.md",
        "RELEASE_NOTES_v2.5.3_BUILD6.md",
        "COVERAGE_REPORT_v2.5.3_BUILD6.md",
        "TEST_AUDIT_REPORT_v2.5.3_BUILD6.md",
        "HARDWARE_VALIDATION_v2.5.3_BUILD6.md",
        "PRE_HARDWARE_AUDIT_REPORT_v2.5.3_BUILD6.md",
        "BUILD_NOTES_v2.9.0_RELEASE.md",
        "RELEASE_MANIFEST_v2.9.0.md",
        "RELEASE_NOTES_v2.9.0.md",
        "COVERAGE_REPORT_v2.9.0.md",
        "TEST_AUDIT_REPORT_v2.9.0.md",
        "HARDWARE_VALIDATION_v2.9.0.md",
        "PRE_HARDWARE_AUDIT_REPORT_v2.9.0.md",
        "BUILD_NOTES_v2.9.1_BUILD1.md",
        "RELEASE_MANIFEST_v2.9.1_BUILD1.md",
        "RELEASE_NOTES_v2.9.1_BUILD1.md",
        "COVERAGE_REPORT_v2.9.1_BUILD1.md",
        "TEST_AUDIT_REPORT_v2.9.1_BUILD1.md",
        "HARDWARE_VALIDATION_v2.9.1_BUILD1.md",
        "PRE_HARDWARE_AUDIT_REPORT_v2.9.1_BUILD1.md",
        "BUILD_NOTES_v2.9.1_BUILD2.md",
        "RELEASE_MANIFEST_v2.9.1_BUILD2.md",
        "RELEASE_NOTES_v2.9.1_BUILD2.md",
        "COVERAGE_REPORT_v2.9.1_BUILD2.md",
        "TEST_AUDIT_REPORT_v2.9.1_BUILD2.md",
        "HARDWARE_VALIDATION_v2.9.1_BUILD2.md",
        "PRE_HARDWARE_AUDIT_REPORT_v2.9.1_BUILD2.md",
        "BUILD_NOTES_v2.9.1_BUILD3.md",
        "RELEASE_MANIFEST_v2.9.1_BUILD3.md",
        "RELEASE_NOTES_v2.9.1_BUILD3.md",
        "COVERAGE_REPORT_v2.9.1_BUILD3.md",
        "TEST_AUDIT_REPORT_v2.9.1_BUILD3.md",
        "HARDWARE_VALIDATION_v2.9.1_BUILD3.md",
        "PRE_HARDWARE_AUDIT_REPORT_v2.9.1_BUILD3.md",
    ]


def _manifest_relpath(root: Path, manifest: Path) -> str:
    return manifest.relative_to(root).as_posix()


def discover_evidence_manifests(root: Path) -> list[Path]:
    evidence_root = root / RELEASE_EVIDENCE_ROOT
    if not evidence_root.exists():
        return []
    return sorted(evidence_root.glob("*/MANIFEST.txt"))


def read_evidence_manifest(root: Path, manifest: Path) -> list[str]:
    entries: list[str] = []
    for raw_line in manifest.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("/") or ".." in Path(line).parts:
            raise ValueError(
                f"unsafe evidence manifest entry in {_manifest_relpath(root, manifest)}: {line}"
            )
        entries.append(Path(line).as_posix())
    return entries


def discover_manifest_evidence(root: Path) -> list[str]:
    required: list[str] = []
    seen: set[str] = set()
    for manifest in discover_evidence_manifests(root):
        manifest_rel = _manifest_relpath(root, manifest)
        for rel in [manifest_rel, *read_evidence_manifest(root, manifest)]:
            if rel not in seen:
                required.append(rel)
                seen.add(rel)
    return required


def required_release_files(root: Path) -> list[str]:
    required: list[str] = []
    seen: set[str] = set()
    for rel in [*legacy_required_release_files(), *discover_manifest_evidence(root)]:
        if rel not in seen:
            required.append(rel)
            seen.add(rel)
    return required


def audit_release_files(root: Path, expected_version: str | None = None) -> list[dict[str, str]]:
    required = required_release_files(root)
    results = []
    for rel in required:
        resolved = resolve_release_artifact(root, rel)
        if resolved is None:
            results.append(fail(f"file:{rel}", "missing"))
        elif resolved == root / rel:
            results.append(ok(f"file:{rel}", "present"))
        else:
            results.append(ok(f"file:{rel}", f"present at {resolved.relative_to(root).as_posix()}"))
    if expected_version:
        addon_path = root / "addon.xml"
        addon_text = addon_path.read_text(encoding="utf-8")
        first_line = addon_text.splitlines()[0].strip() if addon_text.splitlines() else ""
        if first_line.startswith("<?xml") and 'version="1.0"' not in first_line:
            results.append(
                fail(
                    "addon_xml_declaration",
                    f'XML declaration must use version="1.0", found: {first_line}',
                )
            )
        else:
            results.append(ok("addon_xml_declaration", "version=1.0"))
        try:
            actual_version = ET.parse(addon_path).getroot().attrib.get("version")
        except Exception as exc:
            actual_version = None
            results.append(fail("addon_version", f"could not parse addon.xml: {exc}"))
        else:
            results.append(
                ok("addon_version", expected_version)
                if actual_version == expected_version
                else fail("addon_version", f"expected {expected_version}, found {actual_version}")
            )
    return results


def _run_audit_dicts(root: Path, expected_version: str | None = None) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    results.append(audit_compile(root))
    results.extend(audit_xml(root))
    results.extend(audit_locales(root))
    results.append(audit_settings_strings(root))
    results.append(audit_command_map(root))
    results.append(audit_hardware_count(root))
    results.append(audit_coverage_gate(root))
    results.extend(audit_version_source(root, expected_version=expected_version))
    results.extend(audit_release_files(root, expected_version=expected_version))
    return results


def collect_audit_checks(root: Path, expected_version: str | None = None) -> list[AuditCheck]:
    """Collect audit results as typed checks for reporter/CI consumers."""
    return [
        AuditCheck.from_mapping(item)
        for item in _run_audit_dicts(root, expected_version=expected_version)
    ]


def run_audit(root: Path, expected_version: str | None = None) -> list[dict[str, str]]:
    """Return legacy dict audit results for compatibility with existing tests/users."""
    return [
        item.as_dict() for item in collect_audit_checks(root, expected_version=expected_version)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run release audits for script.oppo203.iso.external"
    )
    parser.add_argument("--root", default=".", help="project root; defaults to current directory")
    parser.add_argument("--expected-version", default=None, help="expected addon.xml version")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args(argv)

    root = project_root(Path(args.root))
    checks = collect_audit_checks(root, expected_version=args.expected_version)
    failed = [item for item in checks if not item.passed]
    reporter = JsonReporter() if args.json else TextReporter()
    print(reporter.render(root, checks))
    return 1 if failed else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
