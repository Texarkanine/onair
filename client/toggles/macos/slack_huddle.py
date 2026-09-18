# Slack huddle toggle. This module reads Slack UI through macOS Accessibility.
# The process that starts this toggle must have Accessibility permission.
# This toggle does not activate Slack.

import time
from typing import Callable, Optional

from lib.log_config import get_logger
from toggles.macos.lib.slack_huddle_ax import inspect_slack_huddle

logger = get_logger(__name__)


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
            detail = (
                f"running={running} huddle={huddle} inspectable={inspectable} "
                f"ax_windows={report.get('ax_windows')} "
                f"(start {start_hits}/{start_threshold}, stop {stop_hits}/{stop_threshold})"
            )

            if not running:
                # Slack is not running. A huddle on this Mac is not possible.
                start_hits = 0
                stop_hits = stop_threshold
            elif huddle:
                start_hits = min(start_threshold, start_hits + 1)
                stop_hits = 0
            elif inspectable:
                start_hits = 0
                stop_hits = min(stop_threshold, stop_hits + 1)
            else:
                # Slack is running. The UI is not readable (other Space).
                # Keep the last confirmed state. Do not activate Slack.
                logger.info(f"Slack huddle unreadable (holding state): {detail}")
                time.sleep(poll_interval_s)
                continue

            if not on_call:
                if start_hits >= start_threshold:
                    logger.info(f"Slack huddle started: {detail}")
                    result = callback(True)
                    if result is not None:
                        on_call = result
            else:
                if stop_hits >= stop_threshold:
                    logger.info(f"Slack huddle ended: {detail}")
                    result = callback(False)
                    if result is not None:
                        on_call = result

            if was_on_call == on_call:
                if on_call:
                    logger.info(f"Still in a Slack huddle: {detail}")
                else:
                    logger.info(f"Not in a Slack huddle: {detail}")

            time.sleep(poll_interval_s)

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            time.sleep(5)
            continue
