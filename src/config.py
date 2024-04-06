import os
import logging
import json
from dotenv import load_dotenv
from logger import Logger

load_dotenv()


class ConfigError(Exception):
    pass


def _env(key: str, default: str = None) -> str:
    if os.environ.get(key) is not None:
        return os.environ.get(key)
    if os.environ.get(key.lower()) is not None:
        return os.environ.get(key.lower())
    if os.environ.get(key.upper()) is not None:
        return os.environ.get(key.upper())
    if default is not None:
        return default
    raise ConfigError(f"Environment Error: The '{key}' environment variable does not exist.")


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
    Logger.log("Migrating files from v1.0.1 to v1.1.0...", {"level": "debug"})

    # Adding missing 'webhooks' property to 'watchlist.json'
    file = open(_env("WATCHER_DIRECTORY", "") + "/watchlist.json", "r")
    watchlist = json.loads(file.read())
    file.close()

    for entry in watchlist['watchlist']:
        if 'webhooks' not in entry:
            entry['webhooks'] = []
            Logger.log(f"Added 'webhooks' property to watchlist entry: {entry['name']}.", {"level": "debug"})

    file = open(_env("WATCHER_DIRECTORY", "") + "/watchlist.json", "w")
    file.write(json.dumps(watchlist, indent=4))
    file.close()

    # Adding sample webhook entry to 'webhooks.json', if empty
    file = open(_env("WATCHER_DIRECTORY", "") + "/webhooks.json", "r")
    webhooks = json.loads(file.read())
    file.close()

    if len(webhooks['webhooks']) == 0:
        webhooks['webhooks'].append(_new_webhook_entry_sample())
        file = open(_env("WATCHER_DIRECTORY", "") + "/webhooks.json", "w")
        file.write(json.dumps(webhooks, indent=4))
        file.close()

    Logger.log("Migrated to v1.1.0.", {"level": "debug"})


def _migrate_v111_to_v112() -> None:
    Logger.log("Migrating files from v1.1.1 to v1.1.2...", {"level": "debug"})

    # Adding 'version' property to 'config.json'
    file = open(_env("WATCHER_DIRECTORY", "") + "/config.json", "r")
    config = json.loads(file.read())
    file.close()

    config['version'] = "1.1.2"

    file = open(_env("WATCHER_DIRECTORY", "") + "/config.json", "w")
    file.write(json.dumps(config, indent=4))
    file.close()

    Logger.log("Migrated to v1.1.2.", {"level": "debug"})


def _verify_config_parse() -> None:
    path = _env("WATCHER_DIRECTORY", "") + "/config.json"

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

    if ['nyaa_rss', 'watcher_interval_seconds'] not in config:
        raise ConfigError("Parse Error: 'nyaa_rss' and/or 'watcher_interval_seconds' is missing from config.json. Change the properties and restart the watcher.")

    if config['nyaa_rss'] == "https://nyaa.si/?page=rss&u=NYAA_USERNAME":
        raise ConfigError("Parse Error: No Nyaa RSS found. Add a Nyaa RSS URL to 'config.json' and restart the watcher.")

    if int(config['watcher_interval_seconds']) % 1 != 0 or int(config['watcher_interval_seconds']) < 60:
        raise ConfigError("Parse Error: WATCHER_INTERVAL_SEC must be an integer equal to or greater than 60 seconds.")


def _verify_watchlist_parse() -> None:
    path = _env("WATCHER_DIRECTORY", "") + "/watchlist.json"

    if os.path.exists(path) is False:
        Logger.log("Cannot find 'watchlist.json'. Creating file...")
        file = open(path, "x")
        file.write(json.dumps(_new_watchlist_json(), indent=4))
        file.close()
        Logger.log("Created 'watchlist.json'.")

    file = open(path, "r")
    watchlist = json.loads(file.read())
    file.close()

    if len(watchlist['watchlist']) == 0:
        raise ConfigError("Parse Error: watchlist.json contains no entries. Add entries and restart the watcher.")

    for entry in watchlist['watchlist']:
        if ['name', 'tags', 'regex', 'webhooks'] not in entry:
            raise ConfigError("Parse Error: One or more entries in 'watchlist.json' contains missing or invalid properties. Change the properties and restart the watcher.")

        if entry['name'] == "" and len(entry['tags']) + len(entry['regex']) == 0 \
                or len(entry['tags']) + len(entry['regex']) == 0:
            raise ConfigError("Parse Error: One or more entries in 'watchlist.json' does not have a tag or regex. "
                              "Change the entries to have at least one 'tag' or 'regex' value and restart the watcher.")


def _verify_history_parse() -> None:
    path = _env("WATCHER_DIRECTORY", "") + "/history.json"

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
        raise ConfigError("Parse Error: One or more entries in history.json contains missing or invalid properties. Fix the history properties and restart the watcher.")


def _verify_webhooks_parse() -> None:
    path = _env("WATCHER_DIRECTORY", "") + "/webhooks.json"

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
        if _verify_webhook_entry(webhook) is False:
            raise ConfigError("Parse Error: One or more webhooks in webhooks.json contains missing or invalid properties. Change the properties and restart the watcher.")

        notifications_check = _verify_webhook_notifications(webhook['notifications'], webhook['name'])
        if notifications_check['result'] is False:
            raise ConfigError(f"Parse Error: {notifications_check['message']}. Change the properties and restart the watcher.")

        if webhook['url'] == "https://discord.com/api/webhooks/RANDOM_STRING/RANDOM_STRING":
            Logger.log("Watcher Message: Enter a Discord webhook URL in webhooks.json to be notified when new torrents are downloaded.", {"hint": True})


def _verify_webhook_entry(webhook: dict) -> bool:
    properties = ['name', 'url', 'notifications']
    if not all(key in webhook for key in properties):
        return False
    return True


def _verify_webhook_notifications(webhook_notifications: dict, webhook_name: str) -> dict:
    properties = ['title', 'description', 'show_downloads', 'show_seeders', 'show_leechers', 'show_published',
                  'show_category', 'show_size']
    if not all(key in webhook_notifications for key in properties):
        return {
            "result": False,
            "message": f"'{webhook_name}' webhook contains one or more 'show_' properties that are missing or invalid. Change the webhook properties and restart the watcher"
        }

    if not all(value in range(0, 7) for value in webhook_notifications):
        return {
            "result": False,
            "message": f"'{webhook_name}' webhook contains one or more 'show_' properties out of range (0 to 6). Change the webhook properties and restart the watcher"
        }

    values = [value for value in webhook_notifications if value != 0]
    if len(values) != len(set(values)):
        return {
            "result": False,
            "message": f"'{webhook_name}' webhook contains one or more duplicate 'show_' properties. Change the webhook properties and restart the watcher"
        }

    return {"result": True}


class Config:
    def __init__(self) -> None:
        Logger.log("Verifying files...", {"level": "debug"})
        _verify_config_parse()
        _verify_watchlist_parse()
        _verify_history_parse()
        _verify_webhooks_parse()
        Logger.log("Files verified.", {"level": "debug"})

        version = self.get_config()['version'] if 'version' in self.get_config() else "1.0.1"
        if version == "1.0.1":
            _migrate_v101_to_v110()
            version = "1.1.1"  # Skips v1.1.0
        if version == "1.1.1":
            _migrate_v111_to_v112()
            version = "1.1.2"
        Logger.log(f"Watcher version: {version}", {"level": "debug"})

    @staticmethod
    def append_to_history(torrents: dict | list) -> None:
        file = open(_env("WATCHER_DIRECTORY", "") + "/history.json", "r")
        history = json.loads(file.read())
        file.close()

        history['history'].append(torrents)

        file = open(_env("WATCHER_DIRECTORY", "") + "/history.json", "w")
        file.write(json.dumps(history, indent=4))
        file.close()
        Logger.log(f"Appended '{len(torrents)}' torrents to 'history.json'.", {"level": "debug"})

    @staticmethod
    def get_config() -> dict:
        file = open(_env("WATCHER_DIRECTORY", "") + "/config.json", "r")
        config = json.loads(file.read())
        file.close()
        return config

    @staticmethod
    def get_nyaa_rss() -> str:
        if os.environ.get("NYAA_RSS"):
            return os.environ.get("NYAA_RSS")

        file = open(_env("WATCHER_DIRECTORY", "") + "/config.json", "r")
        config = json.loads(file.read())
        file.close()
        return config['nyaa_rss']

    @staticmethod
    def get_watcher_watchlist() -> dict:
        file = open(_env("WATCHER_DIRECTORY", "") + "/watchlist.json", "r")
        watchlist = json.loads(file.read())
        file.close()
        return watchlist

    @staticmethod
    def get_watcher_history() -> dict:
        file = open(_env("WATCHER_DIRECTORY", "") + "/history.json", "r")
        history = json.loads(file.read())
        file.close()
        return history

    @staticmethod
    def get_watcher_interval() -> int:
        if os.environ.get("WATCHER_INTERVAL_SEC"):
            return int(os.environ.get("WATCHER_INTERVAL_SEC"))

        file = open(_env("WATCHER_DIRECTORY", "") + "/config.json", "r")
        config = json.loads(file.read())
        file.close()
        return int(config['watcher_interval_seconds'])

    @staticmethod
    def get_discord_webhooks() -> dict:
        file = open(_env("WATCHER_DIRECTORY", "") + "/webhooks.json", "r")
        webhooks = json.loads(file.read())
        file.close()
        return webhooks
