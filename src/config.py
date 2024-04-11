import os
import json
from datetime import datetime
from dotenv import load_dotenv
from logger import Logger
from env import Env
from math import floor

load_dotenv()
env = Env()


def _get_version() -> str:
    file = open(env.path("config"), "r")
    config = json.loads(file.read())
    file.close()

    version = config['version']
    if version:
        return version

    file = open(env.path("webhooks"), "r")
    webhooks = json.loads(file.read())
    file.close()

    if len(webhooks['webhooks']) > 0:
        return "1.1.1"
    return "1.0.1"


def _new_config_json() -> dict:
    return {
        "nyaa_rss": "https://nyaa.si/?page=rss&u=NYAA_USERNAME",
        "watcher_interval_seconds": 600,
        "version": "1.1.2"
    }


def _new_watchlist_json() -> dict:
    return {
        "watchlist": [
            {
                "name": "",
                "tags": [],
                "regex": [],
                "webhooks": []
            }
        ]
    }


def _new_webhook_entry_sample() -> dict:
    return {
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


def _new_webhook_json() -> dict:
    return {
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


def _migrate_v101_to_v110() -> None:
    Logger.log("Migrating from v1.0.1 to v1.1.0...")

    # Adding missing 'webhooks' property to 'watchlist.json'
    file = open(env.path("watchlist"), "r")
    watchlist = json.loads(file.read())
    file.close()

    for entry in watchlist['watchlist']:
        if 'webhooks' not in entry:
            entry['webhooks'] = []
            Logger.log(f"Added 'webhooks' property to watchlist entry: {entry['name']}.", {"level": "debug"})

    file = open(env.path("watchlist"), "w")
    file.write(json.dumps(watchlist, indent=4))
    file.close()

    # Adding sample webhook entry to 'webhooks.json', if empty
    file = open(env.path("webhooks"), "r")
    webhooks = json.loads(file.read())
    file.close()

    if len(webhooks['webhooks']) == 0:
        webhooks['webhooks'].append(_new_webhook_entry_sample())
        file = open(env.path("webhooks"), "w")
        file.write(json.dumps(webhooks, indent=4))
        file.close()

    Logger.log("Migrated to v1.1.0.")


def _migrate_v111_to_v112() -> None:
    Logger.log("Migrating from v1.1.1 to v1.1.2...")

    # Adding 'version' property to 'config.json'
    file = open(env.path("config"), "r")
    config = json.loads(file.read())
    file.close()

    config['version'] = "1.1.2"

    file = open(env.path("config"), "w")
    file.write(json.dumps(config, indent=4))
    file.close()

    Logger.log("Migrated to v1.1.2.")


def _verify_config_parse() -> None:
    path = env.path("config")

    if os.path.exists(path) is False:
        Logger.log("Cannot find 'config.json'. Creating file...")
        file = open(path, "x")
        file.write(json.dumps(_new_config_json(), indent=4))
        file.close()
        Logger.log("Created 'config.json'.")
        return

    file = open(path, "r")
    config = json.loads(file.read())
    file.close()

    if not config['nyaa_rss'] or not config['watcher_interval_seconds']:
        raise Exception("Parse Error: 'nyaa_rss' and/or 'watcher_interval_seconds' is missing from 'config.json'. Change the properties and restart the watcher.")

    if config['nyaa_rss'] == "https://nyaa.si/?page=rss&u=NYAA_USERNAME":
        raise Exception("Parse Error: No Nyaa RSS found. Add a Nyaa RSS URL to 'config.json' and restart the watcher.")

    if not isinstance(config['watcher_interval_seconds'], int) or int(config['watcher_interval_seconds']) % 1 != 0:
        raise Exception("Parse Error: 'watcher_interval_seconds' must be an integer equal to or greater than 60 seconds. Change the property and restart the watcher.")

    if int(config['watcher_interval_seconds']) <= 60:
        raise Exception("Parse Error: 'watcher_interval_seconds' must be equal to or greater than 60 seconds. Change the property and restart the watcher.")

    valid_versions = ["1.0.0", "1.0.1", "1.1.1", "1.1.2"]
    if config['version'] and config['version'] not in valid_versions:
        raise Exception(f"Parse Error: v{config['version']} is not a valid version. Change the property to '1.1.1' in 'config.json' and restart the watcher to migrate to v1.1.2.")


def _verify_watchlist_parse() -> None:
    path = env.path("watchlist")

    if os.path.exists(path) is False:
        Logger.log("Cannot find 'watchlist.json'. Creating file...")
        file = open(path, "x")
        file.write(json.dumps(_new_watchlist_json(), indent=4))
        file.close()
        Logger.log("Created 'watchlist.json'.")

    file = open(path, "r")
    watchlist = json.loads(file.read())
    file.close()

    if not watchlist['watchlist'] or len(watchlist['watchlist']) == 0:
        raise Exception("Parse Error: watchlist.json contains no entries. Add entries and restart the watcher.")

    for entry in watchlist['watchlist']:
        if not all(entry['name'] and entry['tags'] and entry['regex'] and entry['webhooks']):
            raise Exception("Parse Error: One or more entries in 'watchlist.json' contains missing or invalid properties. Change the properties and restart the watcher.")

        if entry['name'] == "" and len(entry['tags']) + len(entry['regex']) == 0 \
                or len(entry['tags']) + len(entry['regex']) == 0:
            raise Exception("Parse Error: One or more entries in 'watchlist.json' does not have a tag or regex. "
                              "Change the entries to have at least one 'tag' or 'regex' value and restart the watcher.")


def _verify_history_parse() -> None:
    path = env.path("history")

    if os.path.exists(path) is False:
        Logger.log("Cannot find 'history.json'. Creating file...")
        file = open(path, "x")
        history = {"history": []}
        file.write(json.dumps(history, indent=4))
        file.close()
        Logger.log("Created 'history.json'.")
        return

    file = open(path, "r")
    history = json.loads(file.read())
    file.close()

    properties = ['torrent_title', 'date_downloaded', 'nyaa_page', 'nyaa_hash']
    if not all(all(key in entry for key in properties) for entry in history['history']):
        raise Exception("Parse Error: One or more entries in history.json contains missing or invalid properties. Fix the history properties and restart the watcher.")


def _verify_webhooks_parse() -> None:
    path = env.path("webhooks")

    if os.path.exists(path) is False:
        Logger.log("Cannot find 'webhooks.json'. Creating file...")
        file = open(path, "x")
        file.write(json.dumps(_new_webhook_json(), indent=4))
        file.close()
        Logger.log("Created 'webhooks.json'.")
        return

    file = open(path, "r")
    webhooks = json.loads(file.read())
    file.close()

    for webhook in webhooks['webhooks']:
        entry = _verify_webhook_entry(webhook)
        if entry.get('result') is False:
            raise Exception(f"Parse Error: {entry.get('message')}")

        if webhook['url'] == "https://discord.com/api/webhooks/RANDOM_STRING/RANDOM_STRING":
            Logger.log("Watcher Message: Enter a Discord webhook URL in webhooks.json to be notified when new torrents are downloaded.", {"hint": True})


def _verify_webhook_entry(webhook: dict) -> dict:
    properties = ['name', 'url', 'notifications']
    for key in properties:
        if key not in webhook:
            return {
                "result": False,
                "message": "One or more webhooks in webhooks.json contains missing or invalid properties. Change the properties and restart the watcher."
            }

    notify_properties = ['title', 'description', 'show_downloads', 'show_seeders', 'show_leechers', 'show_published', 'show_category', 'show_size']
    for key in notify_properties:
        if key not in webhook['notifications']:
            return {
                "result": False,
                "message": f"'{webhook['name']}' webhook contains one or more 'show_' properties that are missing or invalid. Change the webhook properties and restart the watcher"
            }

    notify_values: list = [value for key, value in webhook['notifications'].items() if isinstance(value, int)]
    for value in notify_values:
        if value not in range(0, 7):
            return {
                "result": False,
                "message": f"'{webhook['name']}' webhook contains one or more 'show_' properties out of range (0 to 6). Change the webhook properties and restart the watcher"
            }

    if len(notify_values) != len(set(notify_values)):
        return {
            "result": False,
            "message": f"'{webhook['name']}' webhook contains one or more duplicate 'show_' properties. Change the webhook properties and restart the watcher"
        }

    return {"result": True}


class Config:
    @staticmethod
    def verify_and_migrate() -> None:
        Logger.debug("Verifying files...")
        _verify_config_parse()
        _verify_watchlist_parse()
        _verify_history_parse()
        _verify_webhooks_parse()
        Logger.debug("Files verified.")

        version = _get_version()
        if version == "1.0.1":
            _migrate_v101_to_v110()
            version = "1.1.1"  # Skips v1.1.0
        if version == "1.1.1":
            _migrate_v111_to_v112()
            version = "1.1.2"
        Logger.debug(f"Watcher version: {version}")

    @staticmethod
    def append_to_history(torrents: list) -> None:
        file = open(env.path("history"), "r")
        history = json.loads(file.read())
        file.close()

        for torrent in torrents:
            history['history'].append({
                "torrent_title": torrent['title'],
                "date_downloaded": str(datetime.now()),
                "nyaa_page": torrent['id'],
                "nyaa_hash": torrent['nyaa_infohash']
            })

        file = open(env.path("history"), "w")
        file.write(json.dumps(history, indent=4))
        file.close()
        Logger.debug(f"Appended {len(torrents)} torrent{'' if len(torrents) == 1 else 's'} to 'history.json'.")

    @staticmethod
    def get_config() -> dict:
        file = open(env.path("config"), "r")
        config = json.loads(file.read())
        file.close()
        return config

    @staticmethod
    def get_interval_string(interval: int) -> str:
        days = floor(interval / 86400)
        if days > 0:
            interval -= floor(days * 86400)

        hours = floor(interval / 3600)
        if hours > 0:
            interval -= floor(hours * 3600)

        minutes = floor(interval / 60)
        if minutes > 0:
            interval -= floor(minutes * 60)

        seconds = interval

        array = [days, hours, minutes, seconds]

        # Find last non-zero index
        last_index = -1
        i = 0
        while i <= 3:
            if array[i] > 0:
                last_index = i
            i += 1

        # Number of units to display
        units = 0
        for value in array:
            if value > 0:
                units += 1

        # Build string
        if units == 1:
            if days > 0:
                return f"{days} day" if days == 1 else f"{days} days"
            elif hours > 0:
                return f"{hours} hour" if hours == 1 else f"{hours} hours"
            elif minutes > 0:
                return f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"
            else:
                return f"{seconds} second" if seconds == 1 else f"{seconds} seconds"
        else:
            string = ""

            # Days
            if array[0] > 0:
                string += f"{days} day" if days == 1 else f"{days} days"
                if last_index != 0:
                    string += ", "
                units -= 1
            # Hours
            if array[1] > 0:
                if last_index == 1 and units == 1:
                    string += f"and {hours} hour" if hours == 1 else f"and {hours} hours"
                else:
                    string += f"{hours} hour" if hours == 1 else f"{hours} hours"
                    if last_index != 1:
                        string += ", "
                    units -= 1
            # Minutes
            if array[2] > 0:
                if last_index == 2 and units == 1:
                    string += f"and {minutes} minute" if minutes == 1 else f"and {minutes} minutes"
                else:
                    string += f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"
                    if last_index != 2:
                        string += ", "
                    units -= 1
            # Seconds
            if array[3] > 0:
                string += f"and {seconds} second" if seconds == 1 else f"and {seconds} seconds"

            return string

    @staticmethod
    def get_nyaa_rss() -> str:
        if os.environ.get("NYAA_RSS"):
            return os.environ.get("NYAA_RSS")

        file = open(env.path("config"), "r")
        config = json.loads(file.read())
        file.close()
        return config['nyaa_rss']

    @staticmethod
    def get_watcher_watchlist() -> dict:
        file = open(env.path("watchlist"), "r")
        watchlist = json.loads(file.read())
        file.close()
        return watchlist

    @staticmethod
    def get_watcher_history() -> dict:
        file = open(env.path("history"), "r")
        history = json.loads(file.read())
        file.close()
        return history

    @staticmethod
    def get_watcher_interval() -> int:
        if os.environ.get("INTERVAL_SEC"):
            return int(os.environ.get("INTERVAL_SEC"))

        file = open(env.path("config"), "r")
        config = json.loads(file.read())
        file.close()
        return int(config['watcher_interval_seconds'])

    @staticmethod
    def get_discord_webhooks() -> dict:
        file = open(env.path("webhooks"), "r")
        webhooks = json.loads(file.read())
        file.close()
        return webhooks

    @staticmethod
    def get_version() -> str:
        return _get_version()
