import os
import requests
import sched
import time
from config import Config
from datetime import datetime
from logger import Logger
from watcher import Watcher
from webhook import Webhook


def download_torrent(torrent: dict) -> dict:
    torrent_title = torrent.get('title') + ".torrent"
    torrent_url = torrent.get('link')

    file_path = os.environ.get("DOWNLOADS_DIR", "/downloads") + "/" + torrent_title
    try:
        response = requests.get(torrent_url)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            time.sleep(0.01)
        return {"status": response.status_code}
    except Exception as e:
        return {"status": 500, "message": str(e)}


def fetch(scheduler: sched, watcher: Watcher, interval: int, webhook: Webhook, reschedule: bool = True) -> None:
    Logger.log("Searching for new torrents...", {"white_lines": "t"})
    torrents = watcher.fetch_new_torrents()

    # No new torrents
    if len(torrents) == 0:
        interval_string = Config.get_interval_string(interval)
        Logger.log(f"Found 0 new torrents.\nSearching for matching torrents in {interval_string}.")
    # New torrents
    else:
        Logger.log(f"Found {len(torrents)} new torrent{'' if len(torrents) == 1 else 's'}. Downloading...")
        successes = list()
        errors = list()

        for torrent in torrents:
            Logger.debug(f" - Downloading: {torrent.get('title')}...")
            download = download_torrent(torrent)
            torrent['download_datetime'] = str(datetime.now())

            if download.get('status') == 200:
                Logger.log(f" - Downloaded: {torrent.get('title')}")
                successes.append(torrent)

                for webhook_name in torrent.get('watcher_webhooks'):
                    webhook.send_notification(webhook_name, torrent)
            else:
                Logger.log(f" - Error: {torrent.get('title')} (HTTP Status Code: {download.get('status')}.")
                if 'message' in download:
                    Logger.debug(f" - {download.get('message')}")
                errors.append(torrent)
            Logger.debug()

        watcher.append_to_history(successes)
        Config.append_to_history(successes, errors)
        interval_string = Config.get_interval_string(interval)
        error_string = f" Finished with {len(errors)} error{'' if len(errors) == 1 else 's'}." if len(
            errors) > 0 else ""
        Logger.log(f"Done!{error_string if len(errors) > 0 else ''}\nSearching for new torrents in {interval_string}.")

    # Schedule next check
    if reschedule:
        scheduler.enter(interval, 1, fetch, (scheduler, watcher, interval, webhook))
