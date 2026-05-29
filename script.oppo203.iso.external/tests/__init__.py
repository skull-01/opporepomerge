"""Test package marker.

Exists so ``python -m unittest discover -s tests`` (which does NOT load
``conftest.py``) installs the ENH-#43 legacy flat-name alias finder before any
test module runs its bare ``import <addon_module>`` lines. Mirrors the bootstrap
in ``conftest.py`` for the pytest path.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _sub in (_ROOT, os.path.join(_ROOT, "resources", "lib"), os.path.join(_ROOT, "tools")):
    if _sub not in sys.path:
        sys.path.insert(0, _sub)

import resources.lib  # noqa: E402,F401  installs the legacy-name alias finder
