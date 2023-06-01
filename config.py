import os
import logging
import json

from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("config")


class ConfigError(Exception):
    pass


def _verify_config(config: dict) -> bool:
    if config['nyaa_rss'] is None or config['watcher_interval_seconds'] is None:
        return False
    return True


def _verify_watchlist(watchlist: dict) -> bool:
    if "watchlist" in watchlist:
        if len(watchlist["watchlist"]) >= 1:
            for entry in watchlist["watchlist"]:
                if entry["name"] is None \
                        or entry["tags"] is None \
                        or entry["regex"] is None \
                        or len(entry["tags"]) == 0 and len(entry["regex"]) == 0:
                    return False
            return True
        else:
            return False
    else:
        return False


def _verify_history(history: dict) -> bool:
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
        else:
            return False
    else:
        return False


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
            config = {"nyaa_rss": "https://nyaa.si/?page=rss&u=NYAA_USERNAME", "watcher_interval_seconds": 600}  # 10 minutes
            file.write(json.dumps(config, indent=4))
            file.close()
            log.info("Created file.")

        # Using environment variable
        if os.environ.get("NYAA_RSS"):
            return os.environ.get("NYAA_RSS")

        file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/config.json", "r")
        config = json.loads(file.read())

        if _verify_config(config):
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
            watchlist = {"watchlist": [{'name': '', 'tags': [], 'regex': ''}]}
            file.write(json.dumps(watchlist, indent=4))
            file.close()
            log.info("Created file.")

        file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/watchlist.json", "r")
        watchlist = json.loads(file.read())

        if _verify_watchlist(watchlist):
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
            file.write(json.dumps(history, indent=4))
            file.close()
            log.info("Created file.")

        file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/history.json", "r")
        history = json.loads(file.read())

        if _verify_history(history):
            return history
        else:
            raise ConfigError("history.json could not be parsed.")

    def get_watcher_interval(self) -> int:
        # Using environment variable
        if os.environ.get("WATCHER_INTERVAL_SEC"):
            return int(os.environ.get("WATCHER_INTERVAL_SEC"))

        # File has already been verified by this point
        file = open(os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/config.json", "r")
        config = json.loads(file.read())

        interval = int(config['watcher_interval_seconds'])
        if interval >= 1:
            return interval
        elif interval <= 0:
            raise ConfigError("WATCHER_INTERVAL_SEC must be greater than 0.")
        else:
            raise ConfigError("WATCHER_INTERVAL_SEC must be an integer.")
