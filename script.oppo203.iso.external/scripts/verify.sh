#!/usr/bin/env bash
# Local source verification helper for script.oppo203.iso.external.
# Runs the same release checks used by the handoff build process.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPECTED_VERSION="${EXPECTED_VERSION:-2.9.16}"
cd "$ROOT"
python3 -m py_compile service.py default.py resources/lib/kodi/intercept.py resources/lib/kodi/version.py resources/lib/kodi/disc_classification.py resources/lib/oppo/command_map.py resources/lib/kodi/settings_schema.py tools/i18n_extract.py tools/make_pot.py
python3 tools/sync_version.py --root "$ROOT" --check --expected-version "$EXPECTED_VERSION"
python3 tools/type_check.py --root "$ROOT"
python3 tools/test_layout.py --root "$ROOT" --check
python3 tools/i18n_extract.py --root "$ROOT" --check
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --root "$ROOT" --expected-version "$EXPECTED_VERSION"
