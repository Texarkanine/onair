import importlib
import json
import requests
import argparse
import traceback
import threading
from lib.log_config import setup_logging

logger = setup_logging()

parser = argparse.ArgumentParser(
    prog='client.py',
    description="Determines whether the current user is 'on-air' or not."
)
parser.add_argument('-p', '--push', type=str, required=True, help='The full server or sign endpoint URL to push statuses to.')
parser.add_argument('-t', '--toggle', type=str, action='append', required=True, help='Paths to toggle files to use to toggle status')
args = parser.parse_args()



def changed_oncall(to: bool) -> bool:
    """
    Notify the server about a change in call status.
    
    Args:
        to: The new call status
    Returns:
        bool: The new status if successful, None if the update failed
    """
    try:
        response = requests.put(args.push, data=json.dumps(to), timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad status codes
        logger.debug(f"Successfully updated call status to: {to}")
    except requests.exceptions.HTTPError as he:
        logger.error(f"HTTP error updating call status: {he}")
    except requests.exceptions.RequestException as re:
        logger.error(f"Network error updating call status: {re}")
    except Exception as e:
        logger.error(f"Unexpected error updating call status: {e}")
        logger.debug(traceback.format_exc())  # Full traceback at debug level
    
    return to

threads = list()

for toggle in args.toggle:
    print("Toggle selected: " + toggle)
    newmod = importlib.import_module(toggle)
    t = threading.Thread(target=newmod.run_and_call, args=[changed_oncall])
    t.start()
    threads += [t]

for t in threads:
    t.join()

