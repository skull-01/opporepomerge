#!/usr/bin/env bash
# Local packaging helper for script.oppo203.iso.external.
# Creates the runtime installable ZIP and checksum from the current source tree.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${VERSION:-$(cd "$ROOT" && python3 - <<'PY'
from resources.lib.kodi.version import ADDON_VERSION
print(ADDON_VERSION)
PY
)}"
BUILD_SUFFIX="${BUILD_SUFFIX-}"
OUT_DIR="${OUT_DIR:-$ROOT/dist}"
ADDON_ID="script.oppo203.iso.external"
mkdir -p "$OUT_DIR"
cd "$ROOT"
python3 tools/sync_version.py --root "$ROOT" --check --expected-version "$VERSION"
if [[ -n "$BUILD_SUFFIX" ]]; then
  SUFFIX_PART="-${BUILD_SUFFIX}"
else
  SUFFIX_PART=""
fi
RUNTIME_ZIP="$OUT_DIR/${ADDON_ID}-${VERSION}${SUFFIX_PART}.zip"
python3 tools/package_installable_zip.py --root "$ROOT" --output "$RUNTIME_ZIP"
(
  cd "$OUT_DIR"
  sha256sum "$(basename "$RUNTIME_ZIP")" > "${ADDON_ID}-${VERSION}${SUFFIX_PART}.sha256"
)
python3 - <<'PY'
from pathlib import Path
import zipfile
root = Path.cwd()
import os
out_dir = Path(os.environ.get("OUT_DIR", str(root / "dist")))
addon_id = "script.oppo203.iso.external"
version = os.environ.get("VERSION", "") or __import__("resources.lib.kodi.version", fromlist=["ADDON_VERSION"]).ADDON_VERSION
build_suffix = os.environ.get("BUILD_SUFFIX", "")
suffix_part = f"-{build_suffix}" if build_suffix else ""
dev_zip = out_dir / f"{addon_id}-{version}{suffix_part}-dev-source.zip"
skip_dirs = {".git", ".pytest_cache", "__pycache__"}
skip_suffixes = {".pyc", ".pyo"}
with zipfile.ZipFile(dev_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in skip_dirs for part in rel.parts) or path.suffix in skip_suffixes or rel.name == ".coverage":
            continue
        zf.write(path, f"{addon_id}/{rel.as_posix()}")
print(f"Created {dev_zip}")
PY
printf 'Release package created in %s\n' "$OUT_DIR"
