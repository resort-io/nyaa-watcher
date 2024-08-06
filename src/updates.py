import json
import os
import re
from logger import Logger


def get_json_path(filename: str) -> str:
    """
    Returns a filepath string for a JSON file.
    :param filename: The name of the JSON file (without the file extension).
    :return: A string containing the filepath to the JSON file.
    """

    filepath = f"{'/json/dev.' if os.environ.get('ENV', 'PRODUCTION').lower() == 'development' else '/'}{filename}.json"
    return os.environ.get("WATCHER_DIR", "/watcher") + filepath


def update_files(version: str) -> str:
    version = update_to_v111(version)
    version = update_to_v112(version)
    version = update_to_v120(version)
    version = update_to_v121(version)
    return version


def update_to_v111(version: str) -> str:
    """
    Updates JSON files from v1.0.0/v1.0.1 to v1.1.1.
    :return: Updated `version` param.
    """

    if version != "1.0.0" or version != "1.0.1":
        return version

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
    return "1.1.1"


def update_to_v112(version: str) -> str:
    """
    Updates JSON files from v1.1.0/v1.1.1 to v1.1.2.
    :return: Updated `version` param.
    """

    if version != "1.1.0" or version != "1.1.1":
        return version

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
    return "1.1.2"


def update_to_v120(version: str) -> str:
    """
    Updates JSON files from v1.1.2 to v1.2.0.
    :return: Updated `version` param.
    """

    if version != "1.1.2":
        return version

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
    return "1.2.0"


def update_to_v121(version: str) -> str:
    """
        Updates JSON files from v1.2.0 to v1.2.1.
        :return: Updated `version` param.
        """

    if version != "1.2.0":
        return version

    Logger.debug("Updating to v1.2.1...")

    # Update 'version' value in 'config.json'
    config = {
        "version": "1.2.1"
    }

    file = open(get_json_path("config"), "w")
    file.write(json.dumps(config, indent=4))
    file.close()

    Logger.log("Updated to v1.2.1.")
    return "1.2.1"
