"""Work handed to the main thread from another one waits for its answer, up to a limit."""

import threading
import unittest

import main_thread


def _on_helper_thread(function):
    outcome = []
    worker = threading.Thread(target=lambda: outcome.append(_catch(function)))
    worker.start()
    worker.join()
    return outcome[0]


def _catch(function):
    try:
        return ("value", function())
    except BaseException as exc:
        return ("error", exc)


def _runs_at_once(step):
    threading.Thread(target=step).start()


class MainThreadTests(unittest.TestCase):
    def test_on_the_main_thread_the_callback_runs_directly(self):
        never = lambda step: self.fail("nothing should be scheduled")
        self.assertEqual(main_thread.run(lambda: 7, call_after=never), 7)

    def test_from_another_thread_the_answer_comes_back(self):
        kind, value = _on_helper_thread(lambda: main_thread.run(lambda: 7, call_after=_runs_at_once))
        self.assertEqual((kind, value), ("value", 7))

    def test_an_error_on_the_main_thread_reaches_the_caller(self):
        def broken():
            raise ValueError("no event")

        kind, value = _on_helper_thread(lambda: main_thread.run(broken, call_after=_runs_at_once))
        self.assertEqual(kind, "error")
        self.assertIsInstance(value, ValueError)

    def test_a_busy_main_thread_times_out(self):
        kind, value = _on_helper_thread(
            lambda: main_thread.run(lambda: 7, wait_seconds=0.05, call_after=lambda step: None)
        )
        self.assertEqual(kind, "error")
        self.assertIsInstance(value, main_thread.MainThreadTimeout)


if __name__ == "__main__":
    unittest.main()
