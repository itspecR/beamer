"""Start at login on macOS before 13, where a LaunchAgent stands in for SMAppService."""

import plistlib
import tempfile
import unittest
from pathlib import Path

import launch_agent

BUNDLE = "/Applications/Beamer.app"


class LaunchAgentTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.home = Path(folder.name)

    def test_nothing_installed_reads_as_none(self):
        self.assertIsNone(launch_agent.installed_bundle(self.home))

    def test_install_writes_an_agent_that_opens_the_bundle_hidden(self):
        launch_agent.install(BUNDLE, self.home)
        agent = plistlib.loads(launch_agent.plist_path(self.home).read_bytes())
        self.assertEqual(agent["Label"], launch_agent.LABEL)
        self.assertTrue(agent["RunAtLoad"])
        self.assertEqual(agent["ProgramArguments"], ["/usr/bin/open", "-a", BUNDLE, "--args", "--hidden"])

    def test_installed_bundle_is_read_back(self):
        launch_agent.install(BUNDLE, self.home)
        self.assertEqual(launch_agent.installed_bundle(self.home), BUNDLE)

    def test_agent_lives_in_the_users_launch_agents(self):
        expected = self.home / "Library" / "LaunchAgents" / "uk.co.kalkman.beamer.login.plist"
        self.assertEqual(launch_agent.plist_path(self.home), expected)

    def test_remove_deletes_the_agent_and_tolerates_a_missing_one(self):
        launch_agent.install(BUNDLE, self.home)
        launch_agent.remove(self.home)
        launch_agent.remove(self.home)
        self.assertIsNone(launch_agent.installed_bundle(self.home))

    def test_a_damaged_agent_reads_as_installed_elsewhere(self):
        path = launch_agent.plist_path(self.home)
        path.parent.mkdir(parents=True)
        path.write_bytes(b"not a plist")
        self.assertEqual(launch_agent.installed_bundle(self.home), "")


if __name__ == "__main__":
    unittest.main()
