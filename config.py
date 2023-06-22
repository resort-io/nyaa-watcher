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
    if config['nyaa_rss'] is None or config['watcher_interval_seconds'] is None:
        return False
    return True


def _verify_watchlist_parse(watchlist: dict) -> bool:
    if "watchlist" in watchlist:
        if len(watchlist["watchlist"]) >= 1:
            for entry in watchlist["watchlist"]:
                if entry["name"] is None \
                        or entry["tags"] is None \
                        or entry["regex"] is None:
                    return False
            return True
    return False


def _verify_history_parse(history: dict) -> bool:
    if "history" in history:
        if len(history["history"]) == 0:
            return True
        elif len(history["history"]) >= 1:
            for entry in history["history"]:
                if entry["torrent_title"] is None \
                        or entry["date_downloaded"] is None \
                        or entry["nyaa_page"] is None \
                        or entry["nyaa_hash"] is None:
                    return False
            return True
    return False


def _verify_webhooks_parse(webhooks: dict) -> bool:
    try:
        if len(webhooks["webhooks"]) == 0:
            return True
        else:
            for webhook in webhooks["webhooks"]:
                notifications = webhook["notifications"]

                if webhook["name"] is None \
                        or webhook["url"] is None \
                        or notifications is None \
                        or notifications["title"] is None \
                        or notifications["description"] is None \
                        or notifications["show_downloads"] is None \
                        or notifications["show_seeders"] is None \
                        or notifications["show_leechers"] is None \
                        or notifications["show_published"] is None \
                        or notifications["show_category"] is None \
                        or notifications["show_size"] is None:
                    raise ConfigError("Parse Error: One or more webhooks in webhooks.json contains "
                                      "missing or invalid properties.")

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

        if _verify_config_parse(config):
            return config['nyaa_rss']
        else:
            raise ConfigError("config.json could not be parsed.")

    def get_watcher_watchlist(self) -> dict:
        try:
            file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/watchlist.json", "r")
            file.close()
            log.info("Found watchlist.json.")
        except Exception as e:
            log.info("Cannot find watchlist.json.")
            file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/watchlist.json", "x")
            watchlist = {"watchlist": [{'name': '', 'tags': [], 'regex': []}]}
            file.write(json.dumps(watchlist, indent=2))
            file.close()
            log.info("Created file.")

        file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/watchlist.json", "r")
        watchlist = json.loads(file.read())
        file.close()

        if _verify_watchlist_parse(watchlist):
            return watchlist
        else:
            raise ConfigError("watchlist.json could not be parsed.")

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

        if _verify_history_parse(history):
            return history
        else:
            raise ConfigError("history.json could not be parsed.")

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
