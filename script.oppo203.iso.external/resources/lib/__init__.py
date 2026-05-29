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

import importlib
import sys
from importlib.machinery import ModuleSpec

_PKG = __name__  # "resources.lib"

# Legacy flat module name -> owning sub-package. Keep in sync with the tree.
_BUCKET = {
    # tv/
    "adb_control": "tv",
    "roku_ecp_control": "tv",
    "smartthings_control": "tv",
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
    "version": "kodi",
}


class _AliasLoader:
    def __init__(self, target):
        self._target = target

    def create_module(self, spec):
        module = importlib.import_module(self._target)
        sys.modules[spec.name] = module
        return module

    def exec_module(self, module):
        # Body already executed by the canonical import; never re-run it.
        pass


class _AliasFinder:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith(_PKG + "."):
            short = fullname[len(_PKG) + 1 :]
            if "." not in short and short in _BUCKET:
                return ModuleSpec(fullname, _AliasLoader(f"{_PKG}.{_BUCKET[short]}.{short}"))
        elif fullname in _BUCKET:
            return ModuleSpec(fullname, _AliasLoader(f"{_PKG}.{_BUCKET[fullname]}.{fullname}"))
        return None


if not any(isinstance(_f, _AliasFinder) for _f in sys.meta_path):
    sys.meta_path.insert(0, _AliasFinder())
