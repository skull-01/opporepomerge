"""Minimal Kodi xbmcvfs stub for local tests."""
import os
from pathlib import Path


def translatePath(path):
    text = str(path)
    return text.replace("special://profile", "/tmp/kodi-profile").replace("special://home", "/tmp/kodi-home")


def mkdirs(path):
    Path(translatePath(path)).mkdir(parents=True, exist_ok=True)
    return True


def exists(path):
    return Path(translatePath(path)).exists()


class File:
    def __init__(self, path, mode="r"):
        self.path = translatePath(path)
        Path(os.path.dirname(self.path) or ".").mkdir(parents=True, exist_ok=True)
        self._handle = open(self.path, mode, encoding="utf-8")

    def write(self, data):
        return self._handle.write(str(data))

    def read(self):
        return self._handle.read()

    def close(self):
        return self._handle.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False
