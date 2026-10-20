import plistlib
from pathlib import Path

LABEL = "uk.co.kalkman.beamer.login"
OPEN_TOOL = "/usr/bin/open"
HIDDEN_FLAG = "--hidden"


def plist_path(home=None):
    return Path(home or Path.home()) / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def contents(bundle_path):
    return {
        "Label": LABEL,
        "ProgramArguments": [OPEN_TOOL, "-a", str(bundle_path), "--args", HIDDEN_FLAG],
        "RunAtLoad": True,
    }


def installed_bundle(home=None):
    path = plist_path(home)
    if not path.is_file():
        return None
    try:
        arguments = plistlib.loads(path.read_bytes()).get("ProgramArguments", [])
    except (plistlib.InvalidFileException, ValueError, OSError):
        return ""
    return arguments[2] if len(arguments) > 2 else ""


def install(bundle_path, home=None):
    path = plist_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(plistlib.dumps(contents(bundle_path)))


def remove(home=None):
    plist_path(home).unlink(missing_ok=True)
