import json
import os
import re
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
        Logger.log(f"Done!{error_string if len(errors) > 0 else ''}.")

    # Schedule next check
    if reschedule:
        interval_string = Config.get_interval_string(interval)
        Logger.log(f"Searching for new uploads in {interval_string}.")
        scheduler.enter(interval, 1, fetch, (scheduler, watcher, interval, webhooker))


def get_json_path(filename: str) -> str:
    """
    Returns a filepath string for a JSON file.
    :param filename: The name of the JSON file (without the file extension).
    :return: A string containing the filepath to the JSON file.
    """

    version = f"{'json/dev.' if os.environ.get('ENV', 'PRODUCTION').lower() == 'development' else '/'}{filename}.json"
    return os.environ.get("WATCHER_DIR", "/watcher") + version


def update_to_v111() -> None:
    """
    Updates JSON files from v1.0.0 and v1.0.1 to v1.1.1.
    :return: None
    """

    if Config.version != "1.0.0" or Config.version != "1.0.1":
        return

    Logger.debug("Updating to v1.1.1...")

    # Adding missing 'webhooks' property to 'watchlist.json'
    try:
        file = open(get_json_path("watchlist"), "r")
        watchlist = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("watchlist.json", e.doc, e.pos)

    for entry in watchlist.get('watchlist'):
        if 'webhooks' not in entry:
            entry['webhooks'] = []
            Logger.log(f"Added 'webhooks' property to watchlist entry: {entry.get('name')}.", {"level": "debug"})

    file = open(get_json_path("watchlist"), "w")
    file.write(json.dumps(watchlist, indent=4))
    file.close()

    # Adding sample webhook entry to 'webhooks.json', if empty
    try:
        file = open(get_json_path("webhooks"), "r")
        webhooks = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("webhooks.json", e.doc, e.pos)

    if len(webhooks.get('webhooks')) == 0:
        new_webhook_json = {
            "webhooks": [
                {
                    "name": "Example Webhook Name",
                    "url": "https://discord.com/api/webhooks/RANDOM_STRING/RANDOM_STRING",
                    "notifications": {
                        "title": "",
                        "description": "",
                        "show_category": 3,
                        "show_downloads": 4,
                        "show_leechers": 6,
                        "show_published": 1,
                        "show_seeders": 5,
                        "show_size": 2
                    }
                }
            ]
        }

        file = open(get_json_path("webhooks"), "w")
        file.write(json.dumps(new_webhook_json, indent=4))
        file.close()

    Logger.log("Updated to v1.1.1.")
    Config.version = "1.1.1"


def update_to_v112() -> None:
    """
    Updates JSON files from v1.1.0 and v1.1.1 to v1.1.2.
    :return: None
    """

    if Config.version != "1.1.0" or Config.version != "1.1.1":
        return

    Logger.debug("Updating to v1.1.2...")

    # Adding 'errors' property and changing 'history' to 'downloads' in 'history.json'
    try:
        file = open(get_json_path("history"), "r")
        history = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("history.json", e.doc, e.pos)

    history = {
        "downloads": history.get('history', []),
        "errors": history.get('errors', [])
    }

    file = open(get_json_path("history"), "w")
    file.write(json.dumps(history, indent=4))
    file.close()

    # Change value name and adding 'version' property in 'config.json'
    try:
        file = open(get_json_path("config"), "r")
        config = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("config.json", e.doc, e.pos)

    config = {
        "nyaa_rss": config.get('nyaa_rss', "https://nyaa.si/?page=rss&u=NYAA_USERNAME"),
        "interval_sec": config.get('watcher_interval_seconds', 600),
        "version": "1.1.2"
    }

    file = open(get_json_path("config"), "w")
    file.write(json.dumps(config, indent=4))
    file.close()

    Logger.log("Updated to v1.1.2.")
    Config.version = "1.1.2"


def update_to_v120() -> None:
    """
    Updates JSON files from v1.1.2 to v1.2.0.
    :return: None
    """

    if Config.version != "1.1.2":
        return

    Logger.debug("Updating to v1.2.0...")

    # Get values and update the 'version' value in 'config.json'
    try:
        file = open(get_json_path("config"), "r")
        config = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("config.json", e.doc, e.pos)

    interval = config.get('watcher_interval_seconds', 600)
    rss = config.get('nyaa_rss', "https://nyaa.si/?page=rss&u=USERNAME")

    # Update 'watchlist.json' and switch to 'subscriptions.json'
    try:
        file = open(get_json_path("watchlist"), "r")
        watchlist = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("watchlist.json", e.doc, e.pos)

    username = re.search(r"u=[^&]*", rss).group().replace(r"u=", "")

    new_watchlist = []
    for entry in watchlist.get('watchlist'):
        new_watchlist.append({
            "name": entry.get('name'),
            "tags": entry.get('tags', []),
            "regex": entry.get('regex', []),
            "exclude_regex": entry.get('exclude_regex', []),
            "webhooks": entry.get('webhooks', [])
        })

    subscriptions = {
        "interval_sec": interval,
        "subscriptions": [
            {
                "username": username,
                "rss": rss,
                "watchlist": new_watchlist,
                "previous_hash": ""
            }
        ]
    }

    file = open(get_json_path("subscriptions"), "w")
    file.write(json.dumps(subscriptions, indent=4))
    file.close()

    # Adding 'uploader' property to 'history.json'
    try:
        file = open(get_json_path("history"), "r")
        history = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("history.json", e.doc, e.pos)

    new_history = []
    for entry in history.get('downloads'):
        new_history.append({
            "uploader": entry.get('uploader', username),
            "torrent_title": entry.get('torrent_title'),
            "date_downloaded": entry.get('date_downloaded'),
            "nyaa_page": entry.get('nyaa_page'),
            "nyaa_hash": entry.get('nyaa_hash')
        })

    file = open(get_json_path("history"), "w")
    file.write(json.dumps(new_history, indent=4))
    file.close()

    # Update 'version' value in 'config.json'
    config = {
        "version": "1.2.0"
    }

    file = open(get_json_path("config"), "w")
    file.write(json.dumps(config, indent=4))
    file.close()

    Logger.log("Updated to v1.2.0.")
    Config.version = "1.2.0"
