import threading

try:
    from PyObjCTools import AppHelper
except ImportError:  # pragma: no cover - exercised only off macOS
    AppHelper = None

WAIT_SECONDS = 1.0


class MainThreadTimeout(RuntimeError):
    pass


def run(callback, wait_seconds=WAIT_SECONDS, call_after=None):
    if threading.current_thread() is threading.main_thread():
        return callback()
    done = threading.Event()
    outcome = []

    def step():
        try:
            outcome.append((True, callback()))
        except BaseException as exc:
            outcome.append((False, exc))
        finally:
            done.set()

    (call_after or AppHelper.callAfter)(step)
    if not done.wait(wait_seconds):
        raise MainThreadTimeout(f"the main thread did not answer within {wait_seconds} s")
    succeeded, value = outcome[0]
    if not succeeded:
        raise value
    return value
