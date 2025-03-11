import importlib
import json
import requests
import argparse
import traceback
import threading
from lib.log_config import setup_logging
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_result

logger = setup_logging()

parser = argparse.ArgumentParser(
    prog='client.py',
    description="Determines whether the current user is 'on-air' or not."
)
parser.add_argument('-p', '--push', type=str, required=True, help='The full server or sign endpoint URL to push statuses to.')
parser.add_argument('-t', '--toggle', type=str, action='append', required=True, help='Paths to toggle files to use to toggle status')
args = parser.parse_args()

def is_none(result: Optional[bool]) -> bool:
    return result is None

@retry(
    wait=wait_exponential(multiplier=1, min=1, max=300),  # 1s to 5min
    retry=retry_if_result(is_none),  # retry on None returns
    before_sleep=lambda retry_state: logger.warning(
        f"Server update failed. Backing off for {retry_state.next_action.sleep} seconds"
    )
)
def changed_oncall(to: bool) -> Optional[bool]:
    """
    Notify the server about a change in call status.
    
    Args:
        to: The new call status
    Returns:
        Optional[bool]: The new status if successful, None if the update failed
    """
    try:
        response = requests.put(args.push, data=json.dumps(to), timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully updated call status to: {to}")
        return to
    except requests.exceptions.HTTPError as he:
        logger.error(f"HTTP error updating call status: {he}")
        return None
    except requests.exceptions.RequestException as re:
        logger.error(f"Network error updating call status: {re}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error updating call status: {e}")
        logger.debug(traceback.format_exc())
        return None

threads = list()

for toggle in args.toggle:
    print("Toggle selected: " + toggle)
    newmod = importlib.import_module(toggle)
    t = threading.Thread(target=newmod.run_and_call, args=[changed_oncall])
    t.start()
    threads += [t]

for t in threads:
    t.join()

