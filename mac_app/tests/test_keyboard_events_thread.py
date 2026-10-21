"""macOS 10.15 stops the process when a keyboard event is created off the main thread (SIGILL in
CGEventCreateKeyboardEvent on the link thread), so before macOS 13 every keyboard event the injector
posts is created on the main thread; from 13 on it is created where it is posted, as before."""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import input_injector_mac as injector


class NeedTests(unittest.TestCase):
    def test_before_macos_13_keyboard_events_need_the_main_thread(self):
        for major in (10, 11, 12):
            self.assertTrue(injector.keyboard_events_need_main_thread(major), major)

    def test_from_macos_13_they_do_not(self):
        for major in (13, 14, 26):
            self.assertFalse(injector.keyboard_events_need_main_thread(major), major)

    def test_an_unknown_version_keeps_the_current_behaviour(self):
        self.assertFalse(injector.keyboard_events_need_main_thread(None))


class CreationTests(unittest.TestCase):
    def setUp(self):
        self.quartz = mock.MagicMock()
        patcher = mock.patch.object(injector, "Quartz", self.quartz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_on_old_macos_the_event_is_made_through_the_main_thread(self):
        with mock.patch.object(injector, "_KEY_EVENTS_ON_MAIN_THREAD", True), \
                mock.patch.object(injector.main_thread, "run", side_effect=lambda create: create()) as run:
            event = injector._keyboard_event(0x24, True)
        run.assert_called_once()
        self.quartz.CGEventCreateKeyboardEvent.assert_called_once_with(None, 0x24, True)
        self.assertIs(event, self.quartz.CGEventCreateKeyboardEvent.return_value)

    def test_on_current_macos_the_event_is_made_in_place(self):
        with mock.patch.object(injector, "_KEY_EVENTS_ON_MAIN_THREAD", False), \
                mock.patch.object(injector.main_thread, "run") as run:
            injector._keyboard_event(0x24, False)
        run.assert_not_called()
        self.quartz.CGEventCreateKeyboardEvent.assert_called_once_with(None, 0x24, False)


class EverySiteTests(unittest.TestCase):
    def setUp(self):
        self.quartz = mock.MagicMock()
        self.quartz.kCGEventFlagMaskCommand = 1 << 20
        for patcher in (
            mock.patch.object(injector, "Quartz", self.quartz),
            mock.patch.object(injector, "_keyboard_event", return_value=object()),
            mock.patch.object(injector, "_post"),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(injector._mods_down.clear)
        self.addCleanup(injector._held_codes.clear)

    def test_a_key_is_made_by_the_shared_factory(self):
        injector.inject_key("enter", down=True)
        injector._keyboard_event.assert_called_once_with(0x24, True)
        self.quartz.CGEventCreateKeyboardEvent.assert_not_called()

    def test_text_is_made_by_the_shared_factory(self):
        injector.inject_text("hi")
        self.assertEqual(injector._keyboard_event.call_count, 2)
        self.quartz.CGEventCreateKeyboardEvent.assert_not_called()

    def test_a_shortcut_is_made_by_the_shared_factory(self):
        injector._inject_shortcut("cmd", "space")
        self.assertEqual(injector._keyboard_event.call_count, 4)
        self.quartz.CGEventCreateKeyboardEvent.assert_not_called()

    def test_a_browser_key_is_made_by_the_shared_factory(self):
        injector._inject_browser_key("[")
        self.assertEqual(injector._keyboard_event.call_count, 2)
        self.quartz.CGEventCreateKeyboardEvent.assert_not_called()


if __name__ == "__main__":
    unittest.main()
