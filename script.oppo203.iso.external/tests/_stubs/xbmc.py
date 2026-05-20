"""Minimal Kodi xbmc stub for local tests.

The stub is intentionally small and programmable. It is not shipped as a
runtime dependency for Kodi; it only lets normal Python tests import and
exercise Kodi-bound code paths.
"""

LOGDEBUG = 0
LOGINFO = 1
LOGWARNING = 2
LOGERROR = 3

_logs = []
_info_labels = {}
_builtin_calls = []


def reset():
    _logs.clear()
    _info_labels.clear()
    _builtin_calls.clear()
    Player.reset()


def log(message, level=LOGINFO):
    _logs.append((str(message), level))


def get_logs():
    return list(_logs)


def setInfoLabel(label, value):
    _info_labels[str(label)] = str(value)


def getInfoLabel(label):
    return _info_labels.get(str(label), "")


def executebuiltin(command):
    _builtin_calls.append(str(command))


def get_builtin_calls():
    return list(_builtin_calls)


def sleep(milliseconds):
    return None


class Monitor:
    def __init__(self):
        self._abort = False

    def abortRequested(self):
        return self._abort

    def waitForAbort(self, timeout):
        return self._abort

    def requestAbort(self):
        self._abort = True


class Player:
    _playing = False
    _playing_file = ""
    _stopped = False

    @classmethod
    def configure(cls, playing=False, playing_file=""):
        cls._playing = bool(playing)
        cls._playing_file = str(playing_file)
        cls._stopped = False

    @classmethod
    def reset(cls):
        cls.configure(False, "")

    def isPlaying(self):
        return self.__class__._playing

    def stop(self):
        self.__class__._stopped = True
        self.__class__._playing = False

    def getPlayingFile(self):
        return self.__class__._playing_file
