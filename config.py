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
                            or 'regex' not in entry:
                        raise ConfigError("Parse Error: One or more entries in watchlist.json contains missing or "
                                          "invalid properties. Change the properties and restart the server. "
                                          "('webhooks' is optional)")
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
            file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/config.json", "r")
            file.close()
            log.info("Found config.json.")
        except Exception as e:
            log.info("Cannot find config.json.")
            file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/config.json", "x")
            config = {"nyaa_rss": "https://nyaa.si/?page=rss&u=NYAA_USERNAME",
                      "watcher_interval_seconds": 600}  # 10 minutes
            file.write(json.dumps(config, indent=2))
            file.close()
            log.info("Created file.")

        # Using environment variable
        if os.environ.get("NYAA_RSS"):
            return os.environ.get("NYAA_RSS")

        file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/config.json", "r")
        config = json.loads(file.read())
        file.close()

        _verify_config_parse(config)
        return config['nyaa_rss']

    def get_watcher_watchlist(self) -> dict:
        try:
            file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/watchlist.json", "r")
            file.close()
            log.info("Found watchlist.json.")
        except Exception as e:
            log.info("Cannot find watchlist.json.")
            file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/watchlist.json", "x")
            watchlist = {"watchlist": [{'name': '', 'tags': [], 'regex': [], 'webhooks': []}]}
            file.write(json.dumps(watchlist, indent=2))
            file.close()
            log.info("Created file.")

        file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/watchlist.json", "r")
        watchlist = json.loads(file.read())
        file.close()

        _verify_watchlist_parse(watchlist)
        return watchlist

    def get_watcher_history(self) -> dict:
        try:
            file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/history.json", "r")
            file.close()
            log.info("Found history.json.")
        except Exception as e:
            log.info("Cannot find history.json.")
            file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/history.json", "x")
            history = {"history": []}
            file.write(json.dumps(history, indent=2))
            file.close()
            log.info("Created file.")

        file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/history.json", "r")
        history = json.loads(file.read())
        file.close()

        _verify_history_parse(history)
        return history

    def get_watcher_interval(self) -> int:
        # Using environment variable
        if os.environ.get("WATCHER_INTERVAL_SEC"):
            return int(os.environ.get("WATCHER_INTERVAL_SEC"))

        # File has already been verified by get_nyaa_rss()
        file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/config.json", "r")
        config = json.loads(file.read())
        file.close()

        interval = int(config['watcher_interval_seconds'])
        if interval >= 1:
            return interval
        elif interval <= 0:
            raise ConfigError("WATCHER_INTERVAL_SEC must be greater than 0.")
        else:
            raise ConfigError("WATCHER_INTERVAL_SEC must be an integer.")

    def get_discord_webhooks(self) -> dict:
        try:
            file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/webhooks.json", "r")
            file.close()
            log.info("Found webhooks.json.")
        except Exception as e:
            log.info("Cannot find webhooks.json.")
            file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/webhooks.json", "x")
            webhooks = {"webhooks": []}
            file.write(json.dumps(webhooks, indent=2))
            file.close()
            log.info("Created file.")

        file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/webhooks.json", "r")
        webhooks = json.loads(file.read())
        file.close()

        _verify_webhooks_parse(webhooks)
        return webhooks
