"""Input Monitoring is read through CoreGraphics where it has the call, macOS 11 and later. macOS
10.15 lacks CGPreflightListenEventAccess, so there IOKit's IOHIDCheckAccess answers instead."""

import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


def _listen_access_with(quartz):
    with patch.dict(sys.modules, {"Quartz": quartz}):
        sys.modules.pop("listen_access", None)
        module = importlib.import_module("listen_access")
    sys.modules.pop("listen_access", None)
    return module


def _iokit_library(access):
    library = types.SimpleNamespace(IOHIDCheckAccess=Mock(return_value=access), IOHIDRequestAccess=Mock(return_value=True))
    return library


class CoreGraphicsTests(unittest.TestCase):
    def setUp(self):
        self.quartz = types.SimpleNamespace(
            CGPreflightListenEventAccess=Mock(return_value=1), CGRequestListenEventAccess=Mock()
        )
        self.module = _listen_access_with(self.quartz)

    def test_granted_reads_coregraphics(self):
        self.assertIs(self.module.granted(), True)
        self.quartz.CGPreflightListenEventAccess.assert_called_once_with()

    def test_request_asks_coregraphics(self):
        self.module.request()
        self.quartz.CGRequestListenEventAccess.assert_called_once_with()


class IOKitTests(unittest.TestCase):
    def setUp(self):
        self.module = _listen_access_with(types.SimpleNamespace())

    def _with_library(self, library):
        return patch.object(self.module.ctypes, "CDLL", return_value=library)

    def test_granted_when_iokit_says_granted(self):
        library = _iokit_library(self.module.ACCESS_TYPE_GRANTED)
        with self._with_library(library):
            self.assertTrue(self.module.granted())
        library.IOHIDCheckAccess.assert_called_once_with(self.module.REQUEST_TYPE_LISTEN_EVENT)

    def test_not_granted_when_iokit_says_denied_or_unknown(self):
        for access in (1, 2):
            with self._with_library(_iokit_library(access)):
                self.assertFalse(self.module.granted())

    def test_request_asks_iokit_for_listen_events(self):
        library = _iokit_library(self.module.ACCESS_TYPE_GRANTED)
        with self._with_library(library):
            self.module.request()
        library.IOHIDRequestAccess.assert_called_once_with(self.module.REQUEST_TYPE_LISTEN_EVENT)

    def test_iokit_is_loaded_from_the_system_framework(self):
        with self._with_library(_iokit_library(0)) as cdll:
            self.module.granted()
        cdll.assert_called_once_with("/System/Library/Frameworks/IOKit.framework/IOKit")


class UnavailableTests(unittest.TestCase):
    def setUp(self):
        self.module = _listen_access_with(types.SimpleNamespace())

    def test_without_either_call_input_is_not_blocked(self):
        with patch.object(self.module.ctypes, "CDLL", side_effect=OSError("no IOKit")):
            self.assertTrue(self.module.granted())
            self.module.request()

    def test_an_iokit_without_the_calls_counts_as_unavailable(self):
        with patch.object(self.module.ctypes, "CDLL", return_value=types.SimpleNamespace()):
            self.assertTrue(self.module.granted())


if __name__ == "__main__":
    unittest.main()
