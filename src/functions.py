import os
import requests
import sched
import time
from config import Config
from datetime import datetime
from logger import Logger
from watcher import Watcher
from webhooker import Webhooker


def download_torrent(title: str, url: str) -> dict:
    """
    Downloads a torrent file from a given URL.
    :param title: The title of the torrent for the filename.
    :param url: The URL where the torrent file can be downloaded.
    :return: A dictionary containing the status of the download. If successful, the dictionary's `status` value code will be `200`.
        If an error occurs, the dictionary's `status` value will contain the status code and the `message` value will contain an error message.
    """

    file_path = os.environ.get("DOWNLOADS_DIR", "/downloads") + f"/{title}.torrent"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            time.sleep(0.01)  # Wait for file
        return {"status": response.status_code, "message": "success" if response.status_code == 200 else "Error occurred while downloading."}
    except Exception as e:
        return {"status": 500, "message": str(e)}


def fetch(scheduler: sched, watcher: Watcher, interval: int, webhooker: Webhooker, reschedule: bool = True) -> None:
    """
    Fetches all new torrents and schedules the next check.
    :param scheduler: The scheduler object used to schedule the next check.
    :param watcher: The Watcher object used to fetch all new torrents.
    :param interval: The interval (in seconds) at which to check for new torrents.
    :param webhooker: The Webhooker object used to send Discord notifications.
    :param reschedule: Whether to reschedule the next check (Defaults to `True`).
    :return: None
    """

    new_torrents = watcher.fetch_all_feeds()

    # No new torrents
    if len(new_torrents) == 0:
        Logger.log("Found 0 new uploads.")

    # New torrents
    else:
        Logger.log(f"Found {len(new_torrents)} new upload{'' if len(new_torrents) == 1 else 's'}. Downloading...")

        successes = list()
        errors = list()
        for torrent in new_torrents:
            Logger.debug(f" - Downloading: {torrent.get('title')}...")

            download = download_torrent(torrent.get('title'), torrent.get('link'))
            torrent['download_datetime'] = str(datetime.now())  # Attach download datetime to torrent

            if download.get('status') == 200:
                Logger.log(f" - Downloaded: {torrent.get('title')}")
                successes.append(torrent)

                for webhook_name in torrent.get('webhooks'):
                    webhooker.send_notification(webhook_name, torrent)

            else:
                Logger.log(f" - Error: {torrent.get('title')} (HTTP Status Code: {download.get('status')}.")
                Logger.debug(f" - {download.get('message', 'Unknown error.')}")
                errors.append(torrent)
            Logger.debug()

        watcher.append_to_history(successes)
        Config.append_to_history(successes, errors)

        error_string = f" Finished with {len(errors)} error{'' if len(errors) == 1 else 's'}." if len(errors) > 0 else ""
        Logger.log(f"Done!{error_string if len(errors) > 0 else ''}")

    # Schedule next check
    if reschedule:
        interval_string = Config.get_interval_string(interval)
        Logger.log(f"Searching for new uploads in {interval_string}.")
        scheduler.enter(interval, 1, fetch, (scheduler, watcher, interval, webhooker))
