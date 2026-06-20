"""Minimal Kodi xbmcplugin stub for local tests."""

_calls = []


def reset():
    _calls.clear()


def addDirectoryItem(*args, **kwargs):
    _calls.append(("addDirectoryItem", args, kwargs))
    return True


def endOfDirectory(*args, **kwargs):
    _calls.append(("endOfDirectory", args, kwargs))
    return True


def calls():
    return list(_calls)
