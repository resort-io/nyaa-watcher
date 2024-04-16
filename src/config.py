import os
import json
from logger import Logger


def _get_json_path(filename: str) -> str:
    version = f"{'json/dev.' if os.environ.get('ENV', 'PRODUCTION').lower() == 'development' else '/'}{filename}.json"
    return os.environ.get("WATCHER_DIR", "/watcher") + version


def _get_version() -> str:
    try:
        file = open(_get_json_path("config"), "r")
        config = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("config.json", e.doc, e.pos)

    if config.get('version'):
        return config.get('version')

    if not os.path.exists(_get_json_path("webhooks")):
        return "1.0.1"
    return "1.1.0"


def _generate_files() -> None:
    try:
        if os.path.exists(_get_json_path("config")) is False:
            file = open(_get_json_path("config"), "x")
            file.write(json.dumps(_new_config_json(), indent=4))
            file.close()
            Logger.debug("Generated 'config.json'.")

        if os.path.exists(_get_json_path("watchlist")) is False:
            file = open(_get_json_path("watchlist"), "x")
            file.write(json.dumps(_new_watchlist_json(), indent=4))
            file.close()
            Logger.debug("Generated 'watchlist.json'.")

        if os.path.exists(_get_json_path("history")) is False:
            file = open(_get_json_path("history"), "x")
            file.write(json.dumps(new_history_json(), indent=4))
            file.close()
            Logger.debug("Generated 'history.json'.")

        if os.path.exists(_get_json_path("webhooks")) is False:
            file = open(_get_json_path("webhooks"), "x")
            file.write(json.dumps(_new_webhook_json(), indent=4))
            file.close()
            Logger.debug("Generated 'webhooks.json'.")
    except Exception as e:
        raise ValueError(f"Error generating files: {e}")


def _new_config_json() -> dict:
    return {
        "nyaa_rss": "https://nyaa.si/?page=rss&u=NYAA_USERNAME",
        "interval_sec": 600,
        "version": "1.1.2"
    }


def new_history_json() -> dict:
    return {
        "errors": [],
        "downloads": []
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


def _update_v101_to_v110() -> None:
    Logger.debug("Updating from v1.0.1 to v1.1.0...")

    # Adding missing 'webhooks' property to 'watchlist.json'
    try:
        file = open(_get_json_path("watchlist"), "r")
        watchlist = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("watchlist.json", e.doc, e.pos)

    for entry in watchlist.get('watchlist'):
        if 'webhooks' not in entry:
            entry['webhooks'] = []
            Logger.log(f"Added 'webhooks' property to watchlist entry: {entry.get('name')}.", {"level": "debug"})

    file = open(_get_json_path("watchlist"), "w")
    file.write(json.dumps(watchlist, indent=4))
    file.close()

    # Adding sample webhook entry to 'webhooks.json', if empty
    try:
        file = open(_get_json_path("webhooks"), "r")
        webhooks = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("webhooks.json", e.doc, e.pos)

    if len(webhooks.get('webhooks')) == 0:
        file = open(_get_json_path("webhooks"), "w")
        file.write(json.dumps(_new_webhook_json(), indent=4))
        file.close()

    Logger.log("Updated to v1.1.0.")


def _update_v111_to_v112() -> None:
    Logger.debug("Updating from v1.1.1 to v1.1.2...")

    # Adding 'errors' property and changing 'history' to 'downloads' in 'history.json'
    try:
        file = open(_get_json_path("history"), "r")
        history = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("history.json", e.doc, e.pos)

    history = {
        "downloads": history.get('history', []),
        "errors": history.get('errors', [])
    }

    file = open(_get_json_path("history"), "w")
    file.write(json.dumps(history, indent=4))
    file.close()

    # Change value name and adding 'version' property in 'config.json'
    try:
        file = open(_get_json_path("config"), "r")
        config = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("config.json", e.doc, e.pos)

    config = {
        "nyaa_rss": config.get('nyaa_rss', "https://nyaa.si/?page=rss&u=NYAA_USERNAME"),
        "interval_sec": config.get('watcher_interval_seconds', 600),
        "version": "1.1.2"
    }

    file = open(_get_json_path("config"), "w")
    file.write(json.dumps(config, indent=4))
    file.close()

    Logger.log("Updated to v1.1.2.")


def _verify_config_parse() -> None:
    Logger.debug("Verifying 'config.json'...")
    path = _get_json_path("config")

    if os.path.exists(path) is False:
        Logger.log("Cannot find 'config.json'. Creating file...")
        file = open(path, "x")
        file.write(json.dumps(_new_config_json(), indent=4))
        file.close()
        Logger.log("Created 'config.json'.")
        return
    try:
        file = open(path, "r")
        config = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("config.json", e.doc, e.pos)

    if not config.get('nyaa_rss') or not config.get('interval_sec') or not config.get('version'):
        raise Exception("Parse Error: 'nyaa_rss', 'interval_sec', and/or 'version' is missing from 'config.json'. Change the properties and restart the watcher.")

    if config.get('nyaa_rss') == "https://nyaa.si/?page=rss&u=NYAA_USERNAME":
        raise Exception("Parse Error: No Nyaa RSS found. Add a Nyaa RSS URL to 'config.json' and restart the watcher.")

    if not isinstance(int(config.get('interval_sec')), int):
        raise Exception("Parse Error: 'interval_sec' must be an integer that is at least 60 seconds. Change the property and restart the watcher.")

    if int(config.get('interval_sec')) < 60:
        raise Exception("Parse Error: 'interval_sec' must be at least 60 seconds. Change the property and restart the watcher.")

    valid_versions = ["1.0.0", "1.0.1", "1.1.1", "1.1.2"]
    if config.get('version') and config.get('version') not in valid_versions:
        raise Exception(f"Parse Error: v{config.get('version')} is not a valid version. Change the property to '1.1.1' in 'config.json' and restart the watcher to migrate to v1.1.2.")


def _verify_watchlist_parse() -> None:
    Logger.debug("Verifying 'watchlist.json'...")
    path = _get_json_path("watchlist")

    if os.path.exists(path) is False:
        Logger.log("Cannot find 'watchlist.json'. Creating file...")
        file = open(path, "x")
        file.write(json.dumps(_new_watchlist_json(), indent=4))
        file.close()
        Logger.log("Created 'watchlist.json'.")

    try:
        file = open(path, "r")
        watchlist = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("watchlist.json", e.doc, e.pos)

    if not watchlist.get('watchlist') or len(watchlist.get('watchlist')) == 0:
        raise Exception("Parse Error: watchlist.json contains no entries. Add entries and restart the watcher.")

    for entry in watchlist.get('watchlist'):
        if not all(entry.get('name') and entry.get('tags') and entry.get('regex') and entry.get('webhooks')):
            raise Exception("Parse Error: One or more entries in 'watchlist.json' contains missing or invalid properties. Change the properties and restart the watcher.")

        if entry.get('name') == "" and len(entry.get('tags')) + len(entry.get('regex')) == 0 \
                or len(entry.get('tags')) + len(entry.get('regex')) == 0:
            raise Exception("Parse Error: One or more entries in 'watchlist.json' does not have a tag or regex. "
                              "Change the entries to have at least one 'tag' or 'regex' value and restart the watcher.")


def _verify_history_parse() -> None:
    Logger.debug("Verifying 'history.json'...")
    path = _get_json_path("history")

    if os.path.exists(path) is False:
        Logger.log("Cannot find 'history.json'. Creating file...")
        file = open(path, "x")
        file.write(json.dumps(new_history_json(), indent=4))
        file.close()
        Logger.log("Created 'history.json'.")
        return

    try:
        file = open(path, "r")
        history = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("history.json", e.doc, e.pos)

    # Downloads
    if history.get('downloads'):
        properties = ['torrent_title', 'date_downloaded', 'nyaa_page', 'nyaa_hash']
        if not all(all(key in entry for key in properties) for entry in history.get('downloads')):
            raise Exception("Parse Error: One or more 'download' entries in 'history.json' contains missing or invalid properties. Fix the history properties and restart the watcher.")

    # Errors
    if history.get('errors'):
        properties = ['torrent_title', 'date_failed', 'nyaa_page', 'nyaa_hash']
        if not all(all(key in entry for key in properties) for entry in history.get('errors')):
            raise Exception("Parse Error: One or more 'errors' entries in 'history.json' contains missing or invalid properties. Fix the history properties and restart the watcher.")


def _verify_webhooks_parse() -> None:
    Logger.debug("Verifying 'webhooks.json'...")
    path = _get_json_path("webhooks")

    if os.path.exists(path) is False:
        Logger.log("Cannot find 'webhooks.json'. Creating file...")
        file = open(path, "x")
        file.write(json.dumps(_new_webhook_json(), indent=4))
        file.close()
        Logger.log("Created 'webhooks.json'.")
        return

    try:
        file = open(path, "r")
        webhooks = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("webhooks.json", e.doc, e.pos)

    for webhook in webhooks.get('webhooks'):
        entry = _verify_webhook_entry(webhook)
        if entry.get('result') is False:
            raise Exception(f"Webhook Parse Error: {entry.get('message')}")

        if webhook['url'] == "https://discord.com/api/webhooks/RANDOM_STRING/RANDOM_STRING":
            Logger.log("Create an entry in 'webhooks.json' and enter the name into one or more 'watchlist.json' entries to be notified when new files are downloaded.", {"tip": True})


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
        if key not in webhook.get('notifications'):
            return {
                "result": False,
                "message": f"'{webhook.get('name')}' webhook contains one or more 'show_' properties that are missing or invalid. Change the webhook properties and restart the watcher"
            }

    notify_values: list = [value for key, value in webhook.get('notifications').items() if isinstance(value, int) and value > 0]
    for value in notify_values:
        if value not in range(0, 7):
            return {
                "result": False,
                "message": f"'{webhook.get('name')}' webhook contains one or more 'show_' properties out of range (0 to 6). Change the webhook properties and restart the watcher"
            }

    if len(notify_values) != len(set(notify_values)):
        return {
            "result": False,
            "message": f"'{webhook.get('name')}' webhook contains one or more duplicate 'show_' properties. Change the webhook properties and restart the watcher"
        }

    return {"result": True}


class Config:
    @staticmethod
    def update_and_verify() -> None:
        _generate_files()

        try:
            Logger.log("Checking for updates...")
            if _get_version() != "1.1.2":
                _update_v101_to_v110()
                _update_v111_to_v112()
            Logger.debug("Done checking.")

            Logger.log("Verifying files...")
            _verify_config_parse()
            _verify_watchlist_parse()
            _verify_history_parse()
            _verify_webhooks_parse()
            Logger.debug("Done verifying")

        except json.decoder.JSONDecodeError as e:
            raise json.decoder.JSONDecodeError(e.msg, e.doc, e.pos)

    @staticmethod
    def append_to_history(successes: list, errors: list) -> None:
        file = open(_get_json_path("history"), "r")
        history = json.loads(file.read())
        file.close()

        for success in successes:
            history.get('downloads').append({
                "torrent_title": success.get('title'),
                "date_downloaded": success.get('download_datetime'),
                "nyaa_page": success.get('id'),
                "nyaa_hash": success.get('nyaa_infohash')
            })

        for error in errors:
            history.get('errors').append({
                "torrent_title": error.get('title'),
                "date_failed": error.get('download_datetime'),
                "nyaa_page": error.get('id'),
                "nyaa_hash": error.get('nyaa_infohash')
            })

        file = open(_get_json_path("history"), "w")
        file.write(json.dumps(history, indent=4))
        file.close()
        Logger.debug(f"Appended {len(successes)} download{'' if len(successes) == 1 else 's'} and {len(errors)} error{'' if len(errors) == 1 else 's'} to 'history.json'.")

    @staticmethod
    def get_config() -> dict:
        file = open(_get_json_path("config"), "r")
        config = json.loads(file.read())
        file.close()
        return config

    @staticmethod
    def get_interval_string(interval: int) -> str:
        days, remainder = divmod(interval, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        values = [
            f"{value} {name}" + ("s" if value > 1 else "")
            for value, name in [(days, "day"), (hours, "hour"), (minutes, "minute"), (seconds, "second")]
            if value > 0
        ]

        if len(values) > 1:
            last = values.pop()
            return ", ".join(values) + f"{',' if len(values) > 1 else ''} and " + last
        return values[0]

    @staticmethod
    def get_nyaa_rss() -> str:
        if os.environ.get("NYAA_RSS"):
            return os.environ.get("NYAA_RSS")

        file = open(_get_json_path("config"), "r")
        config = json.loads(file.read())
        file.close()
        return config.get('nyaa_rss')

    @staticmethod
    def get_watcher_watchlist() -> dict:
        file = open(_get_json_path("watchlist"), "r")
        watchlist = json.loads(file.read())
        file.close()
        return watchlist

    @staticmethod
    def get_watcher_history() -> dict:
        file = open(_get_json_path("history"), "r")
        history = json.loads(file.read())
        file.close()
        return history

    @staticmethod
    def get_watcher_interval() -> int:
        if os.environ.get("INTERVAL_SEC"):
            return int(os.environ.get("INTERVAL_SEC"))

        file = open(_get_json_path("config"), "r")
        config = json.loads(file.read())
        file.close()
        return int(config.get('interval_sec'))

    @staticmethod
    def get_discord_webhooks() -> dict:
        file = open(_get_json_path("webhooks"), "r")
        webhooks = json.loads(file.read())
        file.close()
        return webhooks
