"""Shared test configuration for both pytest and unittest discovery.

Adds resources/lib and tools to sys.path so test modules can import
addon code by short name (e.g. `import discovery`).
"""
import os, sys
_ROOT = os.path.dirname(os.path.abspath(__file__))
for sub in ("resources/lib", "tools", "tests"):
    p = os.path.join(_ROOT, sub)
    if p not in sys.path:
        sys.path.insert(0, p)
