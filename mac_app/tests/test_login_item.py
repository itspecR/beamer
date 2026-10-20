"""The macOS approval path for start at login."""

import unittest
from unittest.mock import Mock, patch
from pathlib import Path

import login_item


class LoginItemTests(unittest.TestCase):
    def test_requires_approval_has_a_clear_status(self):
        self.assertEqual(login_item.status_text(login_item.REQUIRES_APPROVAL), "Requires approval")

    def test_only_an_applications_bundle_is_eligible_for_login(self):
        self.assertTrue(login_item.installed_in_applications("/Applications/Beamer.app"))
        self.assertTrue(login_item.installed_in_applications("/Applications/Utilities/Beamer.app"))
        self.assertTrue(login_item.installed_in_applications(str(Path.home() / "Applications" / "Beamer.app")))
        self.assertFalse(login_item.installed_in_applications("/Downloads/Beamer.app"))
        self.assertFalse(login_item.installed_in_applications("/AppTranslocation/Beamer.app"))

    def test_a_moved_app_can_remove_but_not_add_its_login_item(self):
        path = "/Downloads/Beamer.app"
        self.assertFalse(login_item.can_toggle(login_item.NOT_REGISTERED, path))
        self.assertTrue(login_item.can_toggle(login_item.ENABLED, path))

    def test_non_default_launch_stays_in_the_menu_bar(self):
        self.assertTrue(login_item.is_background_launch(False))
        self.assertFalse(login_item.is_background_launch(True))
        self.assertFalse(login_item.is_background_launch(None))

    def test_opens_login_items_settings(self):
        service = Mock()
        with patch.object(login_item, "SMAppService", service):
            login_item.open_system_settings()
        service.openSystemSettingsLoginItems.assert_called_once_with()

    def test_without_app_service_the_launch_agent_is_used(self):
        with patch.object(login_item, "SMAppService", None), \
                patch.object(login_item.launch_agent, "install") as install, \
                patch.object(login_item, "_bundle_path", return_value="/Applications/Beamer.app"):
            login_item.set_enabled(True)
        install.assert_called_once_with("/Applications/Beamer.app")

    def test_without_app_service_turning_off_removes_the_agent(self):
        with patch.object(login_item, "SMAppService", None), \
                patch.object(login_item.launch_agent, "remove") as remove:
            login_item.set_enabled(False)
        remove.assert_called_once_with()

    def test_with_app_service_the_launch_agent_is_left_alone(self):
        service = Mock()
        service.mainAppService.return_value.registerAndReturnError_.return_value = (True, None)
        with patch.object(login_item, "SMAppService", service), \
                patch.object(login_item.launch_agent, "install") as install:
            login_item.set_enabled(True)
        install.assert_not_called()
        service.mainAppService.return_value.registerAndReturnError_.assert_called_once_with(None)

    def test_launch_agent_status_follows_the_installed_bundle(self):
        here = "/Applications/Beamer.app"
        self.assertEqual(login_item.agent_status(None, here), login_item.NOT_REGISTERED)
        self.assertEqual(login_item.agent_status(here, here), login_item.ENABLED)
        self.assertEqual(login_item.agent_status("/Downloads/Beamer.app", here), login_item.NOT_FOUND)
        self.assertEqual(login_item.agent_status("", here), login_item.NOT_FOUND)

    def test_without_app_service_settings_open_users_and_groups(self):
        with patch.object(login_item, "SMAppService", None), \
                patch.object(login_item.subprocess, "run") as run:
            login_item.open_system_settings()
        run.assert_called_once_with(["/usr/bin/open", login_item.ACCOUNTS_PANE], check=True)


if __name__ == "__main__":
    unittest.main()
