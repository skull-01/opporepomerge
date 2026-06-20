#!/usr/bin/env bash
# Clean-room local CI gate for the script.oppo203.iso.external add-on.
#
# This is the local-first replacement for the cloud `.github/workflows/ci.yml`
# (CI is disabled - see AGENTS.md "CI is local-only"). It is a faithful superset
# of ci.yml's four jobs (test / lint / types / compatibility-smoke):
#
#   * fresh `git clone` of the current HEAD into a throwaway dir - the gate runs
#     against the COMMITTED state, not the dirty worktree (true clean-room);
#   * uv-managed throwaway venvs: Python 3.12 (full gate) + 3.9/3.10 (compat smoke);
#   * Stage A (once, 3.12): ruff check/format, mypy --gate, doc/version/layout/i18n;
#   * Stage B (full, 3.12): py_compile/compileall, full pytest, unittest discover,
#                           serial 99% coverage gate (matches ci.yml - NOT -n auto);
#   * Stage C (compat smoke, 3.9 + 3.10): py_compile + sync_version + targeted pytest;
#   * Stage D (once, 3.12): runtime ZIP + forbidden-prefix audit + dev-source unpack
#                           smoke + audit_release.
#
# Usage (from the repo root on Windows):   wsl bash scripts/ci-local.sh
# One-time prereq:   curl -LsSf https://astral.sh/uv/install.sh | sh
#                    uv python install 3.9 3.10 3.12
set -euo pipefail

EXPECTED_VERSION="${EXPECTED_VERSION:-2.9.17}"
PRIMARY_PY="3.12"
SMOKE_PYS=("3.9" "3.10")
ADDON_ID="script.oppo203.iso.external"

UV="${UV:-$HOME/.local/bin/uv}"
[ -x "$UV" ] || UV="uv"
if ! "$UV" --version >/dev/null 2>&1; then
  echo "ci-local: uv not found. Install once with:" >&2
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh && uv python install 3.9 3.10 3.12" >&2
  exit 1
fi

SRC_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHA="$(git -C "$SRC_ROOT" rev-parse --short HEAD)"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/oppo-cilocal-XXXXXX")"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

echo "ci-local: clean-room clone of $SHA -> $WORK/repo"
git -C "$SRC_ROOT" clone --quiet --no-local "$SRC_ROOT" "$WORK/repo"
git -C "$WORK/repo" checkout --quiet "$SHA"
ROOT="$WORK/repo"
cd "$ROOT"

export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1   # matches ci.yml; keeps the coverage run serial

# Create a throwaway venv for a Python version and install dev deps; sets $PYBIN.
make_venv() {
  local v="$1" vdir="$WORK/venv-$1"
  echo "ci-local: provisioning Python $v venv" >&2
  "$UV" venv -q --python "$v" "$vdir" >&2
  "$UV" pip install -q --python "$vdir/bin/python" -r requirements-dev.txt paramiko >&2
  PYBIN="$vdir/bin"
}

echo ""
echo "== Stage A: lint + types + doc/version/layout/i18n (Python $PRIMARY_PY) =="
make_venv "$PRIMARY_PY"
PY="$PYBIN/python"
export PATH="$PYBIN:$PATH"
ruff check .
ruff format --check .
"$PY" tools/type_check.py --gate
"$PY" tools/render_docs.py --check
"$PY" tools/sync_version.py --check --expected-version "$EXPECTED_VERSION"
"$PY" tools/test_layout.py --check
"$PY" tools/i18n_extract.py --check

echo ""
echo "== Stage B: full suite + serial 99% coverage gate (Python $PRIMARY_PY) =="
"$PY" -m py_compile service.py default.py
"$PY" -m compileall -q resources tools tests
"$PY" -m pytest -q
"$PY" -m unittest discover -s tests -p 'test_*.py' -q
"$PY" -m coverage run -m pytest -q
"$PY" -m coverage report -m

echo ""
echo "== Stage C: compatibility smoke (Python ${SMOKE_PYS[*]}) =="
for v in "${SMOKE_PYS[@]}"; do
  echo "-- compat smoke: Python $v --"
  make_venv "$v"
  SPY="$PYBIN/python"
  "$SPY" -m py_compile service.py default.py
  "$SPY" tools/sync_version.py --check --expected-version "$EXPECTED_VERSION"
  "$SPY" -m pytest -q \
    tests/test_v2910_final_release.py \
    tests/test_github_readiness_g5_tooling_config.py \
    tests/test_github_readiness_g6_ci_hardening.py \
    tests/test_github_readiness_g7_safe_format_cleanup.py \
    tests/test_github_readiness_g8_final_packaging.py
done

echo ""
echo "== Stage D: packaging audit + dev-source unpack smoke (Python $PRIMARY_PY) =="
PY="$WORK/venv-$PRIMARY_PY/bin/python"
DIST="$WORK/dist"
PATH="$WORK/venv-$PRIMARY_PY/bin:$PATH" \
  OUT_DIR="$DIST" BUILD_SUFFIX="cilocal" VERSION="$EXPECTED_VERSION" \
  bash scripts/package_release.sh
"$PY" - "$DIST" "$EXPECTED_VERSION" "$ADDON_ID" <<'PY'
import sys, zipfile
from pathlib import Path

dist, version, addon_id = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
runtime_zip = dist / f"{addon_id}-{version}-cilocal.zip"
forbidden = tuple(
    f"{addon_id}/{d}/" for d in ("tests", "tools", "scripts", "docs", "release-evidence", ".github")
)
with zipfile.ZipFile(runtime_zip) as zf:
    names = zf.namelist()
    bad = [n for n in names if n.startswith(forbidden)]
    zf.testzip()
if bad:
    raise SystemExit("Forbidden runtime ZIP members: " + ", ".join(bad[:20]))
print(f"runtime_zip={runtime_zip.name}; files={len(names)}; forbidden=0")
PY

UNPACK="$WORK/post-unpack"
mkdir -p "$UNPACK"
"$PY" -c "import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" \
  "$DIST/${ADDON_ID}-${EXPECTED_VERSION}-cilocal-dev-source.zip" "$UNPACK"
(
  cd "$UNPACK/$ADDON_ID"
  "$PY" tools/sync_version.py --check --expected-version "$EXPECTED_VERSION"
  "$PY" -m pytest -q \
    tests/test_github_readiness_g5_tooling_config.py \
    tests/test_github_readiness_g6_ci_hardening.py \
    tests/test_github_readiness_g7_safe_format_cleanup.py \
    tests/test_github_readiness_g8_final_packaging.py \
    tests/test_v2910_final_release.py
  "$PY" tools/audit_release.py --expected-version "$EXPECTED_VERSION"
)
"$PY" tools/audit_release.py --expected-version "$EXPECTED_VERSION"

echo ""
echo "ci-local: ALL GREEN ($SHA) - full gate on $PRIMARY_PY; compat smoke on ${SMOKE_PYS[*]}"
