#!/usr/bin/env python3
"""Render managed documentation metadata blocks.

Build 12 introduces a conservative docs metadata pipeline. The tool parses a
small dependency-free YAML subset from docs/sources.yaml and updates only a
clearly marked generated block in README.md, reference.md, and
web-references.md. Existing hand-written documentation remains preserved.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
from typing import Any

DOCS_SOURCE = Path("docs/sources.yaml")
MANAGED_FILES = ("README.md", "reference.md", "web-references.md")
BEGIN_RE = re.compile(r"<!-- BEGIN GENERATED DOCS METADATA -->.*?<!-- END GENERATED DOCS METADATA -->\n?", re.DOTALL)
BEGIN = "<!-- BEGIN GENERATED DOCS METADATA -->"
END = "<!-- END GENERATED DOCS METADATA -->"


def project_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "addon.xml").exists() and (candidate / "resources" / "settings.xml").exists():
            return candidate
    raise RuntimeError("Could not find add-on root containing addon.xml and resources/settings.xml")


def _coerce(value: str) -> Any:
    text = value.strip()
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    if text.isdigit():
        return int(text)
    return text


def load_sources(path: Path) -> dict[str, Any]:
    """Load the narrow docs/sources.yaml subset used by this project.

    Supported shapes are top-level sections, two-space indented scalar fields,
    and two-space list items. This avoids adding a runtime/dev dependency on
    PyYAML while still giving future builds one metadata source for generated
    documentation snippets.
    """
    data: dict[str, Any] = {}
    current: str | None = None
    current_is_list = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and stripped.endswith(":"):
            current = stripped[:-1]
            data[current] = {}
            current_is_list = False
            continue
        if current is None:
            raise ValueError(f"entry outside section: {line}")
        if line.startswith("  - "):
            if not current_is_list:
                data[current] = []
                current_is_list = True
            data[current].append(line[4:].strip())
            continue
        if line.startswith("  ") and ":" in stripped:
            key, value = stripped.split(":", 1)
            if current_is_list:
                raise ValueError(f"mixed list/scalar section: {current}")
            if not isinstance(data[current], dict):
                data[current] = {}
            data[current][key.strip()] = _coerce(value)
            continue
        raise ValueError(f"unsupported docs metadata line: {line}")
    return data


def render_block(data: dict[str, Any], target: str) -> str:
    release = data.get("release", {})
    protected = data.get("protected_behavior", [])
    documents = data.get("managed_documents", [])
    build_id = release.get("build_id", "unknown build")
    title = release.get("title", "documentation metadata")
    hardware_claimed = str(release.get("hardware_validation_claimed", False)).lower()
    runtime_changed = str(release.get("runtime_behavior_changed", False)).lower()
    lines = [
        BEGIN,
        f"### Generated documentation metadata — {build_id}",
        "",
        f"- Target document: `{target}`",
        f"- Cleanup scope: {title}",
        f"- Runtime behavior changed: `{runtime_changed}`",
        f"- Hardware validation claimed: `{hardware_claimed}`",
        f"- Source recommendation: {release.get('source_recommendation', 'internal cleanup roadmap')}",
        "- Managed documents: " + ", ".join(f"`{item}`" for item in documents),
        "",
        "Protected behavior preserved:",
    ]
    lines.extend(f"- {item}" for item in protected)
    lines.extend([END, ""])
    return "\n".join(lines)


def update_document(path: Path, block: str) -> bool:
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    if BEGIN in original and END in original:
        updated = BEGIN_RE.sub(block, original, count=1)
    else:
        separator = "\n\n" if original and not original.endswith("\n\n") else ""
        updated = original + separator + block
    changed = updated != original
    if changed:
        path.write_text(updated, encoding="utf-8")
    return changed


def check_document(path: Path, block: str) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if block in text:
        return True, f"{path.name}: generated metadata block is current"
    return False, f"{path.name}: generated metadata block is missing or stale"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render/check generated documentation metadata blocks")
    parser.add_argument("--root", default=".", help="project root")
    parser.add_argument("--write", action="store_true", help="write generated metadata blocks")
    parser.add_argument("--check", action="store_true", help="check generated metadata blocks")
    args = parser.parse_args(argv)
    root = project_root(Path(args.root))
    source_path = root / DOCS_SOURCE
    data = load_sources(source_path)
    exit_code = 0
    for rel in MANAGED_FILES:
        path = root / rel
        block = render_block(data, rel)
        if args.write:
            changed = update_document(path, block)
            print(f"{'updated' if changed else 'current'}: {rel}")
        if args.check or not args.write:
            ok, detail = check_document(path, block)
            print(("OK" if ok else "FAIL") + f": {detail}")
            if not ok:
                exit_code = 1
    return exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
