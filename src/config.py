import json
import os
from logger import Logger
from updates import get_json_path, update_files


def _generate_files() -> None:
    """
    Generates any missing JSON files.
    :return: None
    """

    try:
        if not os.path.exists(get_json_path("config")):
            file = open(get_json_path("config"), "x")
            file.write(json.dumps(_new_config_json(), indent=4))
            file.close()
            Logger.debug("Generated 'config.json'.")

        if not os.path.exists(get_json_path("history")):
            file = open(get_json_path("history"), "x")
            file.write(json.dumps(_new_history_json(), indent=4))
            file.close()
            Logger.debug("Generated 'history.json'.")

        if not os.path.exists(get_json_path("subscriptions")):
            file = open(get_json_path("subscriptions"), "x")
            file.write(json.dumps(_new_subscriptions_json(), indent=4))
            file.close()
            Logger.debug("Generated 'subscriptions.json'.")

        if not os.path.exists(get_json_path("webhooks")):
            file = open(get_json_path("webhooks"), "x")
            file.write(json.dumps(_new_webhook_json(), indent=4))
            file.close()
            Logger.debug("Generated 'webhooks.json'.")
    except Exception as e:
        raise ValueError(f"Error generating files: {e}")


def _get_file_version() -> str:
    """
    Gets the version of the `config.json` file.
    :return: The version of the `config.json` file.
    """

    try:
        file = open(get_json_path("config"), "r")
        config = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("config.json", e.doc, e.pos)

    if config.get('version'):
        return config.get('version')

    if not os.path.exists(get_json_path("webhooks")):
        return "1.0.1"
    return "1.1.0"


def _new_config_json() -> dict:
    """
    Creates a new 'config.json' dictionary of the latest version.
    :return: A default 'config.json' dictionary.
    """
    return {
        "version": "1.2.0"
    }


def _new_history_json() -> dict:
    """
    Creates a new 'history.json' dictionary of the latest version.
    :return: A default 'history.json' dictionary.
    """

    return {
        "errors": [],
        "downloads": []
    }


def _new_subscriptions_json() -> dict:
    """
    Creates a new 'subscriptions.json' dictionary of the latest version.
    :return: A default 'subscriptions.json' dictionary.
    """

    return {
        "interval_sec": 600,
        "subscriptions": [
            {
                "username": "Username",
                "rss": "https://nyaa.si/?page=rss&u=USERNAME",
                "watchlist": [
                    {
                        "name": "",
                        "tags": [],
                        "regex": [],
                        "exclude_regex": [],
                        "webhooks": []
                    }
                ],
                "previous_hash": ""
            }
        ]
    }


def _new_webhook_json() -> dict:
    """
    Creates a new 'webhooks.json' dictionary of the latest version.
    :return: A default 'webhooks.json' dictionary.
    """

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


def _verify_config_parse() -> None:
    """
    Verifies the 'config.json' file.
    :return: None
    :except json.decoder.JSONDecodeError: If the 'config.json' file cannot be decoded.
    :except Exception: If the 'config.json' file contains invalid properties.
    """

    Logger.debug("Verifying 'config.json'...")
    path = get_json_path("config")

    if not os.path.exists(path):
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

    if not config.get('version'):
        raise Exception("Parse Error: 'version' is missing from 'config.json'. Add the properties and restart the watcher.")

    valid_versions = ["1.0.0", "1.0.1", "1.1.1", "1.1.2", "1.2.0"]
    if config.get('version') and config.get('version') not in valid_versions:
        raise Exception(f"Parse Error: Version '{config.get('version')}' is not a valid version. Change the property to '1.0.0' in 'config.json' and restart the watcher to migrate to v1.2.0.")


def _verify_subscriptions_parse() -> None:
    """
    Verifies the 'subscriptions.json' file.
    :return: None
    :except json.decoder.JSONDecodeError: If the 'subscriptions.json' file cannot be decoded.
    :except Exception: If the 'subscriptions.json' file contains invalid properties.
    """

    Logger.debug("Verifying 'subscriptions.json'...")
    path = get_json_path("subscriptions")

    if not os.path.exists(path):
        Logger.log("Cannot find 'subscriptions.json'. Creating file...")
        file = open(path, "x")
        file.write(json.dumps(_new_subscriptions_json(), indent=4))
        file.close()
        Logger.log("Created 'subscriptions.json'.")

    try:
        file = open(path, "r")
        subscriptions = json.loads(file.read())
        file.close()
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("subscriptions.json", e.doc, e.pos)

    if not subscriptions.get('subscriptions') or len(subscriptions.get('subscriptions')) == 0:
        raise Exception("Parse Error: 'subscriptions.json' contains no entries. Add entries and restart the watcher.")

    if not isinstance(int(subscriptions.get('interval_sec')), int) or int(subscriptions.get('interval_sec')) < 60:
        raise Exception("Parse Error: The 'interval_sec' property is missing or invalid in 'subscriptions.json'. Add the property and restart the watcher.")

    for sub in subscriptions.get('subscriptions'):
        result = _verify_subscriptions_entry(sub)
        if not result.get('result'):
            raise Exception(f"Subscriptions Parse Error: The '{sub.get('username', 'Unknown User')}' subscription has {result.get('message')}. Change the properties in 'subscriptions.json' and restart the watcher.")


def _verify_subscriptions_entry(sub: dict) -> dict:
    """
    Verifies a subscription entry in the 'subscriptions.json' file.
    :param sub: A dictionary of the subscription entry.
    :return: A dictionary with `result` and `message` values for the verification.
    """

    if not sub.get('username') or not sub.get('rss') or not sub.get('watchlist') or sub.get('previous_hash') is None:
        return {
            "result": False,
            "message": "one or more entries that contains missing or invalid 'username', 'rss, 'watchlist', and/or and/or 'previous_hash' properties"
        }

    if sub.get('username') == "USERNAME":
        return {
            "result": False,
            "message": "one or more entries that contains the default 'username' value"
        }

    if sub.get('rss') == "https://nyaa.si/?page=rss&u=NYAA_USERNAME":
        return {
            "result": False,
            "message": "one or more entries that contains the default 'rss' value"
        }

    for watchlist in sub.get('watchlist'):
        if len(watchlist.get('tags', []) + watchlist.get('regex', [])) == 0:
            return {
                "result": False,
                "message": "one or more 'watchlist' entries that contains no 'tags' or 'regex' values."
            }

    return {"result": True, "message": "success"}


def _verify_history_parse() -> None:
    """
    Verifies the 'history.json' file.
    :return: None
    :except json.decoder.JSONDecodeError: If the 'history.json' file cannot be decoded.
    :except Exception: If the 'history.json' file contains invalid properties.
    """

    Logger.debug("Verifying 'history.json'...")
    path = get_json_path("history")

    if not os.path.exists(path):
        Logger.log("Cannot find 'history.json'. Creating file...")
        file = open(path, "x")
        file.write(json.dumps(_new_history_json(), indent=4))
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
    """
    Verifies the 'webhooks.json' file.
    :return: None
    :except json.decoder.JSONDecodeError: If the 'webhooks.json' file cannot be decoded.
    :except Exception: If the 'webhooks.json' file contains invalid properties.
    """

    Logger.debug("Verifying 'webhooks.json'...")
    path = get_json_path("webhooks")

    if not os.path.exists(path):
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
        result = _verify_webhook_entry(webhook)
        if not result.get('result'):
            raise Exception(f"Webhook Parse Error: {result.get('message')}")


def _verify_webhook_entry(webhook: dict) -> dict:
    """
    Verifies a webhook entry in the 'webhooks.json' file.
    :param webhook: A dictionary of the webhook entry.
    :return: A dictionary with `result` and `message` values for the verification.
    """

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

    return {"result": True, "message": "success"}


class Config:

    version: str = "0.0.0"

    @staticmethod
    def update_and_verify() -> None:
        """
        Updates the JSON files and verifies the contents.
        :return: None
        """

        _generate_files()  # Generate missing files

        Logger.log("Checking for updates...")
        Config.version = _get_file_version()
        Config.version = update_files(Config.version)
        Logger.debug("Done checking.")

        Logger.log("Verifying files...")
        _verify_config_parse()
        _verify_subscriptions_parse()
        _verify_history_parse()
        _verify_webhooks_parse()
        Logger.debug("Done verifying.")

    @staticmethod
    def append_to_history(successes: list, errors: list) -> None:
        """
        Appends download and error entries to the 'history.json' file.
        :param successes: A list of dictionaries for successful torrent downloads.
        :param errors: A list of dictionaries for unsuccessful torrent downloads.
        :return: None
        """

        file = open(get_json_path("history"), "r")
        history = json.loads(file.read())
        file.close()

        for success in successes:
            history.get('downloads').append({
                "uploader": success.get('uploader'),
                "torrent_title": success.get('title'),
                "date_downloaded": success.get('download_datetime'),
                "nyaa_page": success.get('id'),
                "nyaa_hash": success.get('nyaa_infohash')
            })

        for error in errors:
            history.get('errors').append({
                "uploader": error.get('uploader'),
                "torrent_title": error.get('title'),
                "date_failed": error.get('download_datetime'),
                "nyaa_page": error.get('id'),
                "nyaa_hash": error.get('nyaa_infohash')
            })

        file = open(get_json_path("history"), "w")
        file.write(json.dumps(history, indent=4))
        file.close()
        Logger.debug(f"Appended {len(successes)} download{'' if len(successes) == 1 else 's'} and {len(errors)} error{'' if len(errors) == 1 else 's'} to 'history.json'.")

    @staticmethod
    def get_interval_string(interval: int) -> str:
        """
        Converts an interval in seconds to a human-readable string.
        :param interval: The interval in seconds.
        :return: A human-readable string of the interval.
        """

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
    def get_subscriptions() -> dict:
        """
        Gets the subscriptions from the 'subscriptions.json' file.
        :return: A dictionary of the subscriptions file.
        """

        file = open(get_json_path("subscriptions"), "r")
        subscriptions = json.loads(file.read())
        file.close()
        return subscriptions

    @staticmethod
    def get_history() -> dict:
        """
        Gets the history from the 'history.json' file.
        :return: A dictionary of the history file.
        """

        file = open(get_json_path("history"), "r")
        history = json.loads(file.read())
        file.close()
        return history

    @staticmethod
    def get_interval() -> int:
        """
        Gets the `INTERVAL_SEC` environment variable if set, or the `interval_sec` value from the 'subscriptions.json' file.
        :return: The `INTERVAL_SEC` or `interval_sec` integer value (Defaults to 600).
        """

        if os.environ.get("INTERVAL_SEC"):
            return int(os.environ.get("INTERVAL_SEC"))

        file = open(get_json_path("subscriptions"), "r")
        config = json.loads(file.read())
        file.close()
        return int(config.get('interval_sec', 600))

    @staticmethod
    def get_webhooks() -> dict:
        """
        Gets the webhooks from the 'webhooks.json' file.
        :return: A dictionary of the webhooks file.
        """

        file = open(get_json_path("webhooks"), "r")
        webhooks = json.loads(file.read())
        file.close()
        return webhooks

    @staticmethod
    def set_previous_hash(sub_name: str, hash_value: str) -> None:
        """
        Sets the previous hash value for a subscription in the 'subscriptions.json'.
        :param sub_name: The name of the subscription.
        :param hash_value: The hash value to set.
        :return: None
        """

        file = open(get_json_path("subscriptions"), "r")
        subscriptions = json.loads(file.read())
        file.close()

        for sub in subscriptions.get('subscriptions'):
            if sub.get('username') == sub_name:
                sub['previous_hash'] = hash_value
                break

        file = open(get_json_path("subscriptions"), "w")
        file.write(json.dumps(subscriptions, indent=4))
        file.close()
