import time
import re
from toggles.macos.lib import macos_utils
from lib.log_config import get_logger  # Updated import path
from typing import Callable, Optional

logger = get_logger(__name__)

def run_and_call(callback: Callable[[bool], Optional[bool]], browser_name: str, poll_interval_s=1, start_threshold=5, cpu_threshold=15):

    on_call = False

    usages = list()

    cpu_threshold_delta = 0

    while True:
        try:
            was_on_call = on_call

            google_meet_open = False
            
            tab_urls = macos_utils.get_chromium_browser_tab_urls(browser_name)
            for tab_url in tab_urls:
                if re.search(r'^https://meet\.google\.com/.*', tab_url):
                    google_meet_open = True
                    break
            
            bluetooth_headset = macos_utils.is_any_bt_headset_connected()
            
            cpusage = macos_utils.get_cpusage_for_process(f"{browser_name} Helper (Renderer).app")
            usages = [cpusage] + usages
        
            load_avg_q = min(5,len(usages))
            load_avg = sum(usages[0:load_avg_q]) / load_avg_q
            long_load_avg_q = min(25,len(usages))
            long_load_avg = sum(usages[0:long_load_avg_q]) / long_load_avg_q

            if len(usages) > 25:
                usages = usages[0:25]
            
            if cpusage > cpu_threshold:
                cpu_threshold_delta = cpu_threshold_delta + 1
                if cpu_threshold_delta > start_threshold:
                    cpu_threshold_delta = start_threshold
            elif cpusage < cpu_threshold:
                cpu_threshold_delta = cpu_threshold_delta - 1
                if cpu_threshold_delta < 0:
                    cpu_threshold_delta = 0
            
            cpu_data = f"{int(cpusage)} {int(load_avg)} {int(long_load_avg)} (likelihood: {cpu_threshold_delta}/{start_threshold})"
            

            if not on_call:
                # Need to detect a call start
                # if google meet open AND headset, that starts a call.
                # if google meet open AND no headset AND high CPU, that starts a call.

                if google_meet_open:
                    logger.info("Google Meet open...")
                    if bluetooth_headset:
                        # google meet open AND a headset? That's a call!
                        logger.info("\t... and there's a bluetooth headset!")
                        logger.info("CALL STARTED")
                        result = callback(True)
                        if result is not None:  # Only update state if callback succeeded
                            on_call = result
                        continue
                    else:
                        logger.info(f"\t... with no headset! CPU Load: {cpu_data}")
                        # google meet open but NO headset? Check CPU usage
                        if cpu_threshold_delta >= start_threshold:
                            # google meet open, no headset, and high CPU? That's a call!
                            logger.info("\t... with high CPU!")
                            logger.info("CALL STARTED")
                            result = callback(True)
                            if result is not None:  # Only update state if callback succeeded
                                on_call = result
                            continue
            else:
                # need to detect a call end
                # if google meet closed, that starts a call
                # if google meet open, AND no headset, AND low cpu, that ends a call
                if not google_meet_open:
                    # no google meet? no call!
                    logger.info("CALL ENDED")
                    result = callback(False)
                    if result is not None:  # Only update state if callback succeeded
                        on_call = result
                    continue
                else:
                    # google meet is open. Are we just idling on the webpage?
                    if not bluetooth_headset:
                        logger.info(f"\t... with no headset! CPU Load: {cpu_data}")
                        if cpu_threshold_delta == 0:
                            # google meet open, no headset, and low CPU? That's the end of a call!
                            logger.info("\t... with low CPU!")
                            logger.info("CALL ENDED")
                            result = callback(False)
                            if result is not None:  # Only update state if callback succeeded
                                on_call = result
                            continue
            
            if was_on_call == on_call:
                if on_call:
                    logger.info("Still on a call...")
                else:
                    logger.info("Not on a call...")

            time.sleep(poll_interval_s)

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            # Sleep briefly before retrying to avoid tight error loops
            time.sleep(5)
            continue
