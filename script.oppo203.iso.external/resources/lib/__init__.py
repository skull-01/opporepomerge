"""Add-on library package.

ENH-#43 reshaped this flat package into hardware-family sub-packages
(``tv`` / ``oppo`` / ``avr`` / ``kodi``). The canonical name of every module
is now ``resources.lib.<bucket>.<module>``.

A deprecation-window compatibility finder keeps the legacy flat names working
so existing importers do not break in lock-step with the move:

* ``resources.lib.<module>``  (dotted legacy)
* ``<module>``                (bare legacy, used by sys.path-based importers
  such as the conftest-pathed test suite, ``service.py`` and
  ``tools/audit_release.py``)

Each legacy name resolves to the **same** module object as its canonical
counterpart (the finder aliases, it never re-loads). The finder imports nothing
at package-import time: importing ``resources.lib`` must stay cheap and must not
trigger ``kodi.installer`` (which runs ``xbmcaddon.Addon()`` at import time).
Aliasing happens lazily, only when a legacy name is actually imported.
"""

from __future__ import annotations

import importlib
import sys
from importlib.machinery import ModuleSpec
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence
    from importlib.abc import Loader
    from types import ModuleType

_PKG = __name__  # "resources.lib"

# Legacy flat module name -> owning sub-package. Keep in sync with the tree.
_BUCKET = {
    # tv/
    "tv_adb_control": "tv",
    "tv_roku_ecp_control": "tv",
    "tv_smartthings_control": "tv",
    "tv_backends": "tv",
    "tv_control": "tv",
    "tv_diagnostics": "tv",
    "tv_presets": "tv",
    # avr/
    "avr_control": "avr",
    "avr_denon_marantz": "avr",
    "avr_onkyo_eiscp": "avr",
    "avr_presets": "avr",
    "avr_sequence": "avr",
    "avr_sony_audio": "avr",
    "avr_types": "avr",
    "avr_yamaha": "avr",
    "avr_diagnostics": "avr",
    # oppo/
    "oppo_control": "oppo",
    "oppo_remote": "oppo",
    "oppo_tcp_client": "oppo",
    "playback_monitor_svm3": "oppo",
    "playback_monitor_http": "oppo",
    "command_map": "oppo",
    "constants": "oppo",
    "discovery": "oppo",
    "reconnect_backoff": "oppo",
    "hardware_capabilities": "oppo",
    "hardware_presets": "oppo",
    "hardware_profiles": "oppo",
    "hardware_validation_readiness": "oppo",
    "path_mapper": "oppo",
    "nas_playback_adapter": "oppo",
    "autoscript_helper": "oppo",
    # kodi/
    "installer": "kodi",
    "intercept": "kodi",
    "disc_classification": "kodi",
    "settings_reader": "kodi",
    "settings_schema": "kodi",
    "keymap_skin": "kodi",
    "playercorefactory_merge": "kodi",
    "i18n": "kodi",
    "diagnostic_logging": "kodi",
    "diagnostic_summary": "kodi",
    "logging_v116": "kodi",
    "diagnostics": "kodi",
    "arch_benchmark": "kodi",
    "preset_manager": "kodi",
    "external_player": "kodi",
    "playback_session": "kodi",
    "version": "kodi",
}


class _AliasLoader:
    def __init__(self, target: str) -> None:
        self._target = target

    def create_module(self, spec: ModuleSpec) -> ModuleType:
        module = importlib.import_module(self._target)
        sys.modules[spec.name] = module
        return module

    def exec_module(self, module: ModuleType) -> None:
        # Body already executed by the canonical import; never re-run it.
        pass


class _AliasFinder:
    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None = None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        if fullname.startswith(_PKG + "."):
            short = fullname[len(_PKG) + 1 :]
            if "." not in short and short in _BUCKET:
                loader = _AliasLoader(f"{_PKG}.{_BUCKET[short]}.{short}")
                return ModuleSpec(fullname, cast("Loader", loader))
        elif fullname in _BUCKET:
            loader = _AliasLoader(f"{_PKG}.{_BUCKET[fullname]}.{fullname}")
            return ModuleSpec(fullname, cast("Loader", loader))
        return None


if not any(isinstance(_f, _AliasFinder) for _f in sys.meta_path):
    sys.meta_path.insert(0, _AliasFinder())
