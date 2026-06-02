"""L11 guard: every AVR backend the configurator DB can emit maps to a known add-on
avr_backend enum (via normalize_avr_backend), so a future DB backend addition cannot silently
fall through to an unrecognized value. Mirrors the players/TV DB consistency guards."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from resources.lib.avr import avr_presets
from resources.lib.kodi import settings_reader as sr

_SRC = json.loads((ROOT / "configurator/src/avr-db/avr-models.json").read_text(encoding="utf-8"))
_DOCS = json.loads((ROOT / "docs/configurator/avr-db/avr-models.json").read_text(encoding="utf-8"))

# Backends that intentionally have no native add-on driver (the configurator writes no
# avr_backend / leaves control disabled for these).
NO_NATIVE_BACKEND = {"custom_command"}


def test_avr_db_src_and_docs_copies_are_identical():
    assert _SRC == _DOCS


def test_avr_db_backends_map_to_a_known_addon_enum():
    valid = set(sr.ENUM_VALUES["avr_backend"])
    declared = set(_SRC["backend_schema"]["allowed_values"])
    for backend in sorted(declared):
        if backend in NO_NATIVE_BACKEND:
            continue
        mapped = avr_presets.normalize_avr_backend(backend)
        assert mapped in valid, (
            f"AVR DB backend {backend!r} normalizes to {mapped!r}, "
            f"not a known add-on avr_backend enum {sorted(valid)}"
        )
