import os
import logging
import json

from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger()


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


def _is_integer(number) -> bool:
    try:
        int(number)
        return True
    except ValueError:
        return False


def _log(message: str, is_hint: bool = False, log_type: str = "info") -> None:
    if log_type == "info":
        if is_hint and _env("SHOW_HINTS", "true") == "true":
            log.info(message)
        else:
            log.info(message)
    elif log_type == "debug":
        if is_hint and _env("SHOW_HINTS", "true") == "true":
            log.debug(message)
        else:
            log.debug(message)


def _new_config_json() -> dict:
    return {
        "nyaa_rss": "https://nyaa.si/?page=rss&u=NYAA_USERNAME",
        "watcher_interval_seconds": 600
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


def _new_webhook_file_json() -> dict:
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
    log.debug("Migrating files from v1.0.1 to v1.1.0...")

    # Adding missing 'webhooks' property to 'watchlist.json'
    file = open(_env("WATCHER_DIRECTORY", "") + "/watchlist.json", "r")
    watchlist = json.loads(file.read())
    file.close()

    for entry in watchlist['watchlist']:
        if 'webhooks' not in entry:
            entry['webhooks'] = []
            log.debug(f"Added 'webhooks' property to watchlist entry: {entry['name']}.")

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

    log.debug("Migrated to v1.1.0.")


def _migrate_v110_to_v111() -> None:
    log.debug("Migrating files from v1.1.0 to v1.1.1...")

    # TODO: Add 'version' to json file.

    log.debug("Migrated to v1.1.1.")


def _verify_config_parse() -> None:
    path = _env("WATCHER_DIRECTORY", "") + "/config.json"

    if os.path.exists(path) is False:
        log.info("Cannot find 'config.json'. Creating file...")
        file = open(_env("WATCHER_DIRECTORY", "") + "/config.json", "x")
        file.write(json.dumps(_new_config_json(), indent=4))
        file.close()
        log.info("Created 'config.json'.")
        return

    file = open(_env("WATCHER_DIRECTORY", "") + "/config.json", "r")
    config = json.loads(file.read())
    file.close()

    if ['nyaa_rss', 'watcher_interval_seconds'] not in config:
        raise ConfigError("Parse Error: 'nyaa_rss' and/or 'watcher_interval_seconds' is missing from config.json. Change the properties and restart the watcher.")

    if config['nyaa_rss'] == "https://nyaa.si/?page=rss&u=NYAA_USERNAME":
        raise ConfigError("Parse Error: No Nyaa RSS found. Add a Nyaa RSS URL to 'config.json' and restart the watcher.")

    if int(config['watcher_interval_seconds']) % 1 != 0 or int(config['watcher_interval_seconds']) < 60:
        raise ConfigError("Parse Error: WATCHER_INTERVAL_SEC must be an integer equal to or greater than 60 seconds.")


def _verify_watchlist_parse(watchlist: dict) -> bool:
    try:
        if 'watchlist' in watchlist:
            if len(watchlist['watchlist']) >= 1:
                for entry in watchlist['watchlist']:
                    if 'name' not in entry \
                            or 'tags' not in entry \
                            or 'regex' not in entry \
                            or 'webhooks' not in entry:
                        raise ConfigError("Parse Error: One or more entries in watchlist.json contains missing or "
                                          "invalid properties. Change the properties and restart the server.")
                return True
            else:
                raise ConfigError("Parse Error: watchlist.json contains no entries. Add entries and restart "
                                  "the server.")
        else:
            raise ConfigError("Parse Error: watchlist.json contains no 'watchlist' array property. Add the property "
                              "and restart the server.")
    except Exception as e:
        raise ConfigError(f"Parse Error: The {str(e)} property is invalid or misspelled in watchlist.json. Change "
                          f"the property and restart the server.")


def _verify_history_parse(history: dict) -> bool:
    try:
        if len(history['history']) == 0:
            return True
        else:
            for entry in history['history']:
                if 'torrent_title' not in entry \
                        or 'date_downloaded' not in entry \
                        or 'nyaa_page' not in entry \
                        or 'nyaa_hash' not in entry:
                    raise ConfigError("Parse Error: One or more entries in history.json contains missing or "
                                      "invalid properties. Revert the changes and restart the server.")
            return True
    except Exception as e:
        raise ConfigError(f"Parse Error: The {str(e)} property is invalid or misspelled in history.json. Change "
                          f"the property and restart the server.")


def _verify_webhooks_parse() -> None:
    path = _env("WATCHER_DIRECTORY", "") + "/webhooks.json"

    if os.path.exists(path) is False:
        log.info("Cannot find 'webhooks.json'. Creating file...")
        file = open(_env("WATCHER_DIRECTORY", "") + "/webhooks.json", "x")
        file.write(json.dumps(_new_webhook_file_json(), indent=4))
        file.close()
        log.info("Created 'webhooks.json'.")
        return

    file = open(_env("WATCHER_DIRECTORY", "") + "/webhooks.json", "r")
    webhooks = json.loads(file.read())
    file.close()

    for webhook in webhooks['webhooks']:
        if _verify_webhook_entry(webhook) is False:
            raise ConfigError("Parse Error: One or more webhooks in webhooks.json contains missing or invalid properties. Change the properties and restart the watcher.")

        notifications_check = _verify_webhook_notifications(webhook['notifications'], webhook['name'])
        if notifications_check['result'] is False:
            raise ConfigError(f"Parse Error: {notifications_check['message']}. Change the properties and restart the watcher.")

        if webhook['url'] == "https://discord.com/api/webhooks/RANDOM_STRING/RANDOM_STRING":
            _log("Watcher Message: Enter a Discord webhook URL in webhooks.json to be notified when new torrents are downloaded.", True)


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
        self.config = dict(os.environ)
        try:
            log.debug("Verifying files...")
            _verify_config_parse()
            _verify_watchlist_parse()
            _verify_history_parse()
            _verify_webhooks_parse()
            log.debug("Files verified.")

            # TODO: Create check for v1.0.1 to v1.1.0
            _migrate_v101_to_v110()

            # TODO: Create check for v1.1.0 to v1.1.1
            # _migrate_v110_to_v111()
        except Exception as e:
            log.info(e, exc_info=True)

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
        try:
            file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/watchlist.json", "r")
            file.close()
            log.info("Found watchlist.json.")
        except Exception as e:
            log.info("Cannot find watchlist.json.")
            file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/watchlist.json", "x")
            watchlist = {"watchlist": [{'name': '', 'tags': [], 'regex': [], 'webhooks': []}]}
            file.write(json.dumps(watchlist, indent=2))
            file.close()
            log.info("Created file.")

        file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/watchlist.json", "r")
        watchlist = json.loads(file.read())
        file.close()

        _verify_watchlist_parse(watchlist)

        # Checking for empty/invalid watchlist entries
        for entry in watchlist['watchlist']:
            if entry['name'] == "" and len(entry['tags']) == 0 and len(entry['regex']) == 0 \
                    or len(entry['tags']) == 0 and len(entry['regex']) == 0:
                raise ConfigError("Watchlist Error: One or more watchlist entries does not have a tag or regex. "
                                  "Add an entry including a title with tag(s) and/or regex(es) to watchlist.json "
                                  "and restart the server.")

        return watchlist

    @staticmethod
    def get_watcher_history() -> dict:
        try:
            file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/history.json", "r")
            file.close()
            log.info("Found history.json.")
        except Exception as e:
            log.info("Cannot find history.json.")
            file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/history.json", "x")
            history = {"history": []}
            file.write(json.dumps(history, indent=2))
            file.close()
            log.info("Created file.")

        file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/history.json", "r")
        history = json.loads(file.read())
        file.close()

        _verify_history_parse(history)
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
