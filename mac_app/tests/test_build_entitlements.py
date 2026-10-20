"""build_dmg.sh reads the bundle python's entitlements before its runtime probe. codesign on macOS
10.15 has no --xml and exits 2 on it, so the plain form is read there instead."""

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

BUILD_SCRIPT = Path(__file__).resolve().parents[1] / "build_dmg.sh"
ENTITLEMENT = "com.apple.security.cs.disable-library-validation"
PLIST = f"<plist><dict><key>{ENTITLEMENT}</key><true/></dict></plist>"
CATALINA_CODESIGN = f"""#!/bin/bash
for arg in "$@"; do [ "$arg" = --xml ] && {{ echo "codesign: unrecognized option '--xml'" >&2; exit 2; }}; done
echo '{PLIST}'
"""
CURRENT_CODESIGN = f"""#!/bin/bash
echo '{PLIST}'
"""
REFUSING_CODESIGN = """#!/bin/bash
exit 1
"""


def _function_source():
    match = re.search(r"^entitlements_of\(\) \{\n.*?^\}\n", BUILD_SCRIPT.read_text(), re.M | re.S)
    return match.group(0)


def _entitlements_with(codesign_script):
    with tempfile.TemporaryDirectory() as folder:
        codesign = Path(folder) / "codesign"
        codesign.write_text(codesign_script)
        codesign.chmod(0o755)
        script = f'{_function_source()}\nentitlements_of /fake/python\n'
        result = subprocess.run(
            ["bash", "-c", script], capture_output=True, text=True,
            env={"PATH": f"{folder}:/usr/bin:/bin"},
        )
    return result.returncode, result.stdout


class EntitlementsTests(unittest.TestCase):
    def test_catalina_codesign_falls_back_to_the_plain_form(self):
        code, output = _entitlements_with(CATALINA_CODESIGN)
        self.assertEqual(code, 0)
        self.assertIn(ENTITLEMENT, output)

    def test_current_codesign_answers_the_xml_form(self):
        code, output = _entitlements_with(CURRENT_CODESIGN)
        self.assertEqual(code, 0)
        self.assertIn(ENTITLEMENT, output)

    def test_a_refusing_codesign_yields_nothing(self):
        code, output = _entitlements_with(REFUSING_CODESIGN)
        self.assertNotEqual(code, 0)
        self.assertEqual(output, "")

    def test_probe_loads_reads_through_the_helper(self):
        self.assertIn('if entitlements_of "$python" | grep -F disable-library-validation', BUILD_SCRIPT.read_text())


if __name__ == "__main__":
    unittest.main()
