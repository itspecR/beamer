import ctypes

import Quartz

IOKIT_PATH = "/System/Library/Frameworks/IOKit.framework/IOKit"
REQUEST_TYPE_LISTEN_EVENT = 1
ACCESS_TYPE_GRANTED = 0


class _CoreGraphics:
    def granted(self):
        return bool(Quartz.CGPreflightListenEventAccess())

    def request(self):
        Quartz.CGRequestListenEventAccess()


class _IOKit:
    def __init__(self, library):
        self.check = library.IOHIDCheckAccess
        self.check.argtypes = [ctypes.c_uint32]
        self.check.restype = ctypes.c_uint32
        self.ask = library.IOHIDRequestAccess
        self.ask.argtypes = [ctypes.c_uint32]
        self.ask.restype = ctypes.c_bool

    def granted(self):
        return self.check(REQUEST_TYPE_LISTEN_EVENT) == ACCESS_TYPE_GRANTED

    def request(self):
        self.ask(REQUEST_TYPE_LISTEN_EVENT)


class _Unavailable:
    def granted(self):
        return True

    def request(self):
        pass


def _iokit():
    try:
        return _IOKit(ctypes.CDLL(IOKIT_PATH))
    except (OSError, AttributeError):
        return None


def backend():
    if hasattr(Quartz, "CGPreflightListenEventAccess"):
        return _CoreGraphics()
    return _iokit() or _Unavailable()


def granted():
    return backend().granted()


def request():
    backend().request()
