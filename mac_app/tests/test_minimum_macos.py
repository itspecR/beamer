"""The app's Info.plist and its launcher are built for the same oldest macOS, macOS 10.15."""

import re
import unittest
from pathlib import Path

MAC_APP = Path(__file__).resolve().parents[1]
CATALINA = "10.15"


def _setup_minimum():
    return re.search(r'^MACOS_MINIMUM = "([0-9.]+)"$', (MAC_APP / "setup.py").read_text(), re.M).group(1)


def _build_minimum():
    return re.search(r"^MACOS_MINIMUM=([0-9.]+)$", (MAC_APP / "build_dmg.sh").read_text(), re.M).group(1)


class MinimumMacOSTests(unittest.TestCase):
    def test_info_plist_admits_catalina(self):
        self.assertEqual(_setup_minimum(), CATALINA)

    def test_launcher_is_built_for_catalina(self):
        self.assertEqual(_build_minimum(), CATALINA)

    def test_plist_reads_the_constant(self):
        self.assertIn('"LSMinimumSystemVersion": MACOS_MINIMUM,', (MAC_APP / "setup.py").read_text())

    def test_launcher_reads_the_constant(self):
        self.assertIn('-mmacosx-version-min="$MACOS_MINIMUM"', (MAC_APP / "build_dmg.sh").read_text())


if __name__ == "__main__":
    unittest.main()
