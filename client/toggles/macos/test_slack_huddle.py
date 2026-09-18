import unittest
from unittest.mock import patch

from toggles.macos.slack_huddle import log_huddle, observation_kind, run_and_call


class ObservationKindTests(unittest.TestCase):
    def test_leave_huddle_empty_windows_is_clear(self):
        """Leave: Slack still running, huddle gone, AXWindows empty."""
        self.assertEqual(
            observation_kind(
                running=True, huddle=False, inspectable=False, ax_windows=0
            ),
            "clear",
        )

    def test_budget_exhausted_with_windows_is_hold(self):
        """Windows exist but the walk was unreadable."""
        self.assertEqual(
            observation_kind(
                running=True, huddle=False, inspectable=False, ax_windows=3
            ),
            "hold",
        )

    def test_huddle_visible_is_huddle(self):
        """A huddle match counts even if inspectable is false."""
        self.assertEqual(
            observation_kind(
                running=True, huddle=True, inspectable=False, ax_windows=0
            ),
            "huddle",
        )

    def test_slack_not_running_is_absent(self):
        """No Slack process means a huddle on this Mac is not possible."""
        self.assertEqual(
            observation_kind(
                running=False, huddle=False, inspectable=False, ax_windows=0
            ),
            "absent",
        )

    def test_readable_no_huddle_is_clear(self):
        """Inspectable Slack with no huddle is a decisive miss."""
        self.assertEqual(
            observation_kind(
                running=True, huddle=False, inspectable=True, ax_windows=2
            ),
            "clear",
        )


class LogHuddleTests(unittest.TestCase):
    def test_info_is_short_and_detail_is_debug(self):
        """Info stays human-readable; the field dump goes to debug."""
        message = "Still in a Slack huddle"
        detail = (
            "running=True huddle=False inspectable=False ax_windows=0 "
            "(start 3/3, stop 0/3)"
        )
        with self.assertLogs("toggles.macos.slack_huddle", level="DEBUG") as captured:
            log_huddle(message, detail)
        levels = {record.levelname: record.getMessage() for record in captured.records}
        self.assertEqual(levels["INFO"], message)
        self.assertEqual(levels["DEBUG"], detail)
        self.assertNotIn("ax_windows=", levels["INFO"])


class RunAndCallTests(unittest.TestCase):
    def test_leave_empty_windows_ends_the_call(self):
        """After a huddle, Leave with zero AX windows must callback False."""
        huddle_on = {
            "ok": True,
            "running": True,
            "huddle": True,
            "inspectable": True,
            "ax_windows": 1,
        }
        leave = {
            "ok": True,
            "running": True,
            "huddle": False,
            "inspectable": False,
            "ax_windows": 0,
        }
        tick = {"n": 0}
        calls = []

        def inspect():
            tick["n"] += 1
            if tick["n"] <= 3:
                return huddle_on
            if tick["n"] <= 6:
                return leave
            raise KeyboardInterrupt()

        def callback(value):
            calls.append(value)
            return value

        with patch(
            "toggles.macos.slack_huddle.inspect_slack_huddle", side_effect=inspect
        ), patch("toggles.macos.slack_huddle.time.sleep"):
            with self.assertRaises(KeyboardInterrupt):
                run_and_call(
                    callback, poll_interval_s=0, start_threshold=3, stop_threshold=3
                )

        self.assertEqual(calls, [True, False])
