"""build_dmg.sh compiles the bundle's loose packages under a relative name, so no .pyc names the
building Mac's home folder. compileall ignores -d for a directory given with a trailing slash."""

import marshal
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BUILD_SCRIPT = Path(__file__).resolve().parents[1] / "build_dmg.sh"
PYC_HEADER = 16


def _compile_line():
    return next(line for line in BUILD_SCRIPT.read_text().splitlines() if "-m compileall" in line)


def _compiled_filename(packages_argument, packages):
    subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "-d", f"lib/{packages.name}", packages_argument],
        check=True, stdout=subprocess.DEVNULL,
    )
    pyc = next(packages.glob("pkg/__pycache__/*.pyc"))
    return marshal.loads(pyc.read_bytes()[PYC_HEADER:]).co_filename


class BytecodePathTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.packages = Path(folder.name) / "lib" / "python3.13"
        (self.packages / "pkg").mkdir(parents=True)
        (self.packages / "pkg" / "mod.py").write_text("VALUE = 1\n")

    def test_script_drops_the_trailing_slash(self):
        self.assertRegex(_compile_line(), re.escape('"${packages%/}"'))

    def test_without_the_slash_the_name_is_relative(self):
        name = _compiled_filename(str(self.packages), self.packages)
        self.assertEqual(name, "lib/python3.13/pkg/mod.py")


if __name__ == "__main__":
    unittest.main()
