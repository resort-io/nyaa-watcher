import os
import logging
import json

from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("config")


class ConfigError(Exception):
    pass


def is_integer(number) -> bool:
    try:
        int(number)
        return True
    except ValueError:
        return False


def _verify_config_parse(config: dict) -> bool:
    try:
        if 'nyaa_rss' not in config or 'watcher_interval_seconds' not in config:
            raise ConfigError("Parse Error: nyaa_rss or watcher_interval_seconds is missing from config.json. "
                              "Add the properties and restart the server.")
        return True
    except Exception as e:
        raise ConfigError(f"Parse Error: The {str(e)} property is invalid or misspelled in config.json. Change "
                          f"the property and restart the server.")


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


def _verify_webhooks_parse(webhooks: dict) -> bool:
    try:
        if len(webhooks['webhooks']) == 0:
            return True
        else:
            for webhook in webhooks['webhooks']:
                if 'name' not in webhook \
                        or 'url' not in webhook \
                        or 'notifications' not in webhook \
                        or 'title' not in webhook['notifications'] \
                        or 'description' not in webhook['notifications'] \
                        or 'show_downloads' not in webhook['notifications'] \
                        or 'show_seeders' not in webhook['notifications'] \
                        or 'show_leechers' not in webhook['notifications'] \
                        or 'show_published' not in webhook['notifications'] \
                        or 'show_category' not in webhook['notifications'] \
                        or 'show_size' not in webhook['notifications']:
                    raise ConfigError("Parse Error: One or more webhooks in webhooks.json contains "
                                      "missing or invalid properties.")

                notifications = webhook['notifications']
                if not is_integer(notifications['show_downloads']) \
                        or not is_integer(notifications['show_seeders']) \
                        or not is_integer(notifications['show_leechers']) \
                        or not is_integer(notifications['show_published']) \
                        or not is_integer(notifications['show_category']) \
                        or not is_integer(notifications['show_size']):
                    raise ConfigError("Parse Error: One or more 'show_' properties in webhooks.json "
                                      "are not in range (0 to 6).")
            return True
    except Exception as e:
        raise ConfigError(f"Parse Error: The {str(e)} property is invalid or misspelled in webhooks.json. Change "
                          f"the property and restart the server.")


class Config:
    def __init__(self) -> None:
        self.config = dict(os.environ)
        try:
            log.debug("Migrating files from v1.0.1 to v1.1.0...")
            self.migrate_v101_to_v110()
            log.debug("Migration complete.")
        except Exception as e:
            log.debug("Migration failed. " + str(e))

    def _get_key(self, key: str, default: str = None):
        if key in self.config:
            return self.config[key]
        elif key.upper() in self.config:
            return self.config[key.upper()]
        elif key.lower() in self.config:
            return self.config[key.lower()]
        elif default is not None:
            return default
        else:
            return False

    def get_nyaa_rss(self) -> str:
        try:
            file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/config.json", "r")
            file.close()
            log.info("Found config.json.")
        except Exception as e:
            log.info("Cannot find config.json.")
            file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/config.json", "x")
            config = {"nyaa_rss": "https://nyaa.si/?page=rss&u=NYAA_USERNAME",
                      "watcher_interval_seconds": 600}  # 10 minutes
            file.write(json.dumps(config, indent=2))
            file.close()
            log.info("Created file.")

        # Using environment variable
        if os.environ.get("NYAA_RSS"):
            return os.environ.get("NYAA_RSS")

        file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/config.json", "r")
        config = json.loads(file.read())
        file.close()

        _verify_config_parse(config)

        if config['nyaa_rss'] == "https://nyaa.si/?page=rss&u=NYAA_USERNAME":
            raise ConfigError("Config Error: No Nyaa RSS found. Add a Nyaa RSS URL to config.json and "
                              "restart the server.")
        return config['nyaa_rss']

    def get_watcher_watchlist(self) -> dict:
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

    def get_watcher_history(self) -> dict:
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

    def get_watcher_interval(self) -> int:
        # Using environment variable
        if os.environ.get("WATCHER_INTERVAL_SEC"):
            return int(os.environ.get("WATCHER_INTERVAL_SEC"))

        # File has already been verified by get_nyaa_rss()
        file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/config.json", "r")
        config = json.loads(file.read())
        file.close()

        interval = int(config['watcher_interval_seconds'])
        if interval >= 60:
            return interval
        elif interval < 60:
            raise ConfigError("WATCHER_INTERVAL_SEC must be equal to or greater than 60 seconds.")
        else:
            raise ConfigError("WATCHER_INTERVAL_SEC must be an integer.")

    def get_discord_webhooks(self) -> dict:
        try:
            file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/webhooks.json", "r")
            file.close()
            log.info("Found webhooks.json.")
        except Exception as e:
            log.info("Cannot find webhooks.json.")
            file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/webhooks.json", "x")
            webhooks = {"webhooks": [
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
            ]}
            file.write(json.dumps(webhooks, indent=2))
            file.close()
            log.info("Created file.")

        file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/webhooks.json", "r")
        webhooks = json.loads(file.read())
        file.close()

        _verify_webhooks_parse(webhooks)

        if len(webhooks['webhooks']) == 0:
            return webhooks

        for webhook in webhooks['webhooks']:
            if webhook['url'] == "https://discord.com/api/webhooks/RANDOM_STRING/RANDOM_STRING":
                log.info("Server Message: Enter a Discord webhook URL in webhooks.json to be notified when new "
                         "torrents are downloaded.")
                continue

            notifications = webhook['notifications']

            # Verifying ranges
            if notifications['show_downloads'] not in range(0, 7) \
                    or notifications['show_seeders'] not in range(0, 7) \
                    or notifications['show_leechers'] not in range(0, 7) \
                    or notifications['show_published'] not in range(0, 7) \
                    or notifications['show_category'] not in range(0, 7) \
                    or notifications['show_size'] not in range(0, 7):
                raise ConfigError(f"Webhook Error: '{webhook['name']}' webhook contains one or more 'show_' "
                                  f"properties out of range (0 to 6). Change the webhook properties in webhook.json "
                                  f"and restart the server.")

            # Verifying no duplicates
            values = list()
            if notifications['show_downloads'] != 0:
                values.append(notifications['show_downloads'])
            if notifications['show_seeders'] != 0:
                values.append(notifications['show_seeders'])
            if notifications['show_leechers'] != 0:
                values.append(notifications['show_leechers'])
            if notifications['show_published'] != 0:
                values.append(notifications['show_published'])
            if notifications['show_category'] != 0:
                values.append(notifications['show_category'])
            if notifications['show_size'] != 0:
                values.append(notifications['show_size'])

            values_set = set(values)
            if len(values_set) != len(values):
                raise ConfigError(f"Webhook Error: '{webhook['name']}' webhook contains one or more duplicate "
                                  f"'show_' properties. Change the webhook properties and restart the server.")

        return webhooks

    def migrate_v101_to_v110(self) -> None:
        # Adding missing 'webhooks' property to 'watchlist.json'
        file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/watchlist.json", "r")
        watchlist = json.loads(file.read())
        file.close()

        for entry in watchlist['watchlist']:
            if 'webhooks' not in entry:
                entry['webhooks'] = []
                log.debug(f"Added 'webhooks' property to watchlist entry: {entry['name']}.")

        file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/watchlist.json", "w")
        file.write(json.dumps(watchlist, indent=2))
        file.close()

        # Adding sample webhook entry to 'webhooks.json', if empty
        file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/webhooks.json", "r")
        webhooks = json.loads(file.read())
        file.close()

        if len(webhooks['webhooks']) == 0:
            sample_webhook = {
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
            webhooks['webhooks'].append(sample_webhook)

            file = open(os.environ.get("WATCHER_DIRECTORY", "") + "/webhooks.json", "w")
            file.write(json.dumps(webhooks, indent=2))
            file.close()
