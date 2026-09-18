# Slack huddle toggle. This module reads Slack UI through macOS Accessibility.
# The process that starts this toggle must have Accessibility permission.
# This toggle does not activate Slack.

import time
from typing import Callable, Optional

from lib.log_config import get_logger
from toggles.macos.lib.slack_huddle_ax import inspect_slack_huddle

logger = get_logger(__name__)


def observation_kind(running, huddle, inspectable, ax_windows):
    """
    Classify one inspector report for the huddle poll loop.

    absent: Slack is not running.
    huddle: a huddle is visible.
    clear: no huddle, and this look is decisive (including zero AX windows).
    hold: Slack is running but the tree was not readable.
    """
    if not running:
        return "absent"
    if huddle:
        return "huddle"
    if inspectable or ax_windows == 0:
        return "clear"
    return "hold"


def log_huddle(message, detail):
    """Log a short human-readable info line; put inspector fields on debug."""
    logger.info(message)
    logger.debug(detail)


def run_and_call(
    callback: Callable[[bool], Optional[bool]],
    poll_interval_s=2,
    start_threshold=3,
    stop_threshold=3,
):
    on_call = False
    start_hits = 0
    stop_hits = 0

    while True:
        try:
            was_on_call = on_call
            report = inspect_slack_huddle()

            if not report.get("ok", False):
                logger.error(f"Slack huddle inspector failed: {report.get('error')}")
                time.sleep(5)
                continue

            running = bool(report.get("running"))
            huddle = bool(report.get("huddle"))
            inspectable = bool(report.get("inspectable"))
            ax_windows = int(report.get("ax_windows") or 0)
            kind = observation_kind(running, huddle, inspectable, ax_windows)
            detail = (
                f"running={running} huddle={huddle} inspectable={inspectable} "
                f"ax_windows={ax_windows} "
                f"(start {start_hits}/{start_threshold}, stop {stop_hits}/{stop_threshold})"
            )

            if kind == "hold":
                # Windows exist but the walk did not finish. Keep the last confirmed
                # state. Do not activate Slack.
                log_huddle("Slack huddle unreadable (holding state)", detail)
                time.sleep(poll_interval_s)
                continue
            if kind == "absent":
                start_hits = 0
                stop_hits = stop_threshold
            elif kind == "huddle":
                start_hits = min(start_threshold, start_hits + 1)
                stop_hits = 0
            else:
                start_hits = 0
                stop_hits = min(stop_threshold, stop_hits + 1)

            if not on_call:
                if start_hits >= start_threshold:
                    log_huddle("CALL STARTED", detail)
                    result = callback(True)
                    if result is not None:
                        on_call = result
            else:
                if stop_hits >= stop_threshold:
                    log_huddle("CALL ENDED", detail)
                    result = callback(False)
                    if result is not None:
                        on_call = result

            if was_on_call == on_call:
                if on_call:
                    log_huddle("Still on a call...", detail)
                else:
                    log_huddle("Not on a call...", detail)

            time.sleep(poll_interval_s)

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            time.sleep(5)
            continue
