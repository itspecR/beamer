"""The running macOS major version, read once for the choices that depend on it."""

import unittest
from unittest import mock

import macos_version


class MacOSVersionTests(unittest.TestCase):
    def test_catalina_reads_as_ten(self):
        with mock.patch.object(macos_version.platform, "mac_ver", return_value=("10.15.7", ("", "", ""), "x86_64")):
            self.assertEqual(macos_version.major(), 10)

    def test_a_current_mac_reads_its_major(self):
        with mock.patch.object(macos_version.platform, "mac_ver", return_value=("26.1", ("", "", ""), "arm64")):
            self.assertEqual(macos_version.major(), 26)

    def test_an_unreadable_version_gives_the_default(self):
        with mock.patch.object(macos_version.platform, "mac_ver", return_value=("", ("", "", ""), "")):
            self.assertIsNone(macos_version.major())
            self.assertEqual(macos_version.major(default=26), 26)


if __name__ == "__main__":
    unittest.main()
