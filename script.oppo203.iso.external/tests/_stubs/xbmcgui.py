"""Minimal Kodi xbmcgui stub for local tests."""

_calls = []
_yesno = []
_select = []
_input = []

NOTIFICATION_INFO = "info"
NOTIFICATION_WARNING = "warning"
NOTIFICATION_ERROR = "error"


def reset():
    _calls.clear()
    _yesno.clear()
    _select.clear()
    _input.clear()


def push_yesno(value):
    _yesno.append(bool(value))


def push_select(index):
    _select.append(int(index))


def push_input(value):
    _input.append(str(value))


def calls():
    return list(_calls)


class Dialog:
    def ok(self, heading, message=""):
        _calls.append(("ok", str(heading), str(message)))
        return True

    def yesno(self, heading, message="", *args, **kwargs):
        _calls.append(("yesno", str(heading), str(message)))
        return _yesno.pop(0) if _yesno else False

    def select(self, heading, options, *args, **kwargs):
        _calls.append(("select", str(heading), list(options or [])))
        return _select.pop(0) if _select else -1

    def input(self, heading, defaultt="", *args, **kwargs):
        _calls.append(("input", str(heading), str(defaultt)))
        return _input.pop(0) if _input else str(defaultt)

    def notification(self, heading, message, icon="", time=0, sound=True):
        _calls.append(("notification", str(heading), str(message), icon, time, sound))
        return True

    def textviewer(self, heading, text):
        _calls.append(("textviewer", str(heading), str(text)))
        return True
