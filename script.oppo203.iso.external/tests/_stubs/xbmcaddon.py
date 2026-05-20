"""Minimal Kodi xbmcaddon stub for local tests."""

_settings = {}
_info = {
    "id": "script.oppo203.iso.external",
    "name": "Oppo UDP-203 ISO External Player",
    "version": "2.0.0.3",
    "path": "/tmp/script.oppo203.iso.external",
    "profile": "/tmp/script.oppo203.iso.external/profile",
}
_localized = {}


def reset(settings=None, info=None, localized=None):
    _settings.clear()
    _settings.update({str(k): str(v) for k, v in dict(settings or {}).items()})
    if info:
        _info.update({str(k): str(v) for k, v in dict(info).items()})
    _localized.clear()
    _localized.update({int(k): str(v) for k, v in dict(localized or {}).items()})


class Addon:
    def __init__(self, id=None):
        self.id = id or _info.get("id", "script.oppo203.iso.external")

    def getAddonInfo(self, key):
        return _info.get(str(key), "")

    def getSetting(self, key):
        return _settings.get(str(key), "")

    def setSetting(self, key, value):
        _settings[str(key)] = str(value)

    def getLocalizedString(self, string_id):
        try:
            sid = int(string_id)
        except Exception:
            return ""
        return _localized.get(sid, "")
