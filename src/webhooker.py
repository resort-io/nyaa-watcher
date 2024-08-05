import discord
import re
from logger import Logger


def _apply_fields(webhook_json: dict, notification: discord.Embed, torrent: dict) -> discord.Embed:
    """
    Applies the 'show_' fields to a notification.
    :param webhook_json: A dictionary of a webhook entry.
    :param notification: A discord.Embed object.
    :param torrent: A dictionary of a torrent entry.
    :return: A discord.Embed object with the applied fields.
    """

    for i in range(1, 7):
        if webhook_json.get('notifications').get('show_downloads') == i:
            notification.add_field(name="Downloads", value=torrent.get('nyaa_downloads'))
        elif webhook_json.get('notifications').get('show_seeders') == i:
            notification.add_field(name="Seeders", value=torrent.get('nyaa_seeders'))
        elif webhook_json.get('notifications').get('show_leechers') == i:
            notification.add_field(name="Leechers", value=torrent.get('nyaa_leechers'))
        elif webhook_json.get('notifications').get('show_published') == i:
            notification.add_field(name="Published", value=re.sub(r":\d\d -0000", "", torrent.get('published')))
        elif webhook_json.get('notifications').get('show_category') == i:
            notification.add_field(name="Category", value=torrent.get('nyaa_category'))
        elif webhook_json.get('notifications').get('show_size') == i:
            notification.add_field(name="Size", value=torrent.get('nyaa_size'))
    return notification


def _insert_tags(string: str, webhook_name: str, torrent: dict) -> str:
    """
    Replaces tags in a string with values torrent and subscription information.
    :param string: The string to replace tags in.
    :param webhook_name: The name of a webhook.
    :param torrent: A dictionary of a torrent entry.
    :return: A string with replaced tags.
    """

    string = string.replace("$webhook", webhook_name) \
        .replace("$title", torrent.get('title')) \
        .replace("$downloads", torrent.get('nyaa_downloads')) \
        .replace("$seeders", torrent.get('nyaa_seeders')) \
        .replace("$leechers", torrent.get('nyaa_leechers')) \
        .replace("$size", torrent.get('nyaa_size')) \
        .replace("$published", re.sub(r":\d\d -0000", "", torrent.get('published'))) \
        .replace("$category", torrent.get('nyaa_downloads')) \
        .replace("$uploader", torrent.get('uploader')) \
        .replace("$watchlist", torrent.get('watchlist'))
    return string


def _parse_url(url: str) -> list:
    """
    Parses a Discord webhook URL to extract the webhook ID and token.
    :param url: A Discord webhook URL.
    :return: A list with the webhook ID and token.
    """

    return (
        url.replace("https://discord.com/api/webhooks/", "")
        .replace("https://discordapp.com/api/webhooks/", "")
        .split("/")
    )


def create_webhook(url: str) -> discord.SyncWebhook | None:
    """
    Creates a Discord webhook object from a webhook URL.
    :param url: The URL of a Discord webhook.
    :return: A Discord webhook object. `None` if the webhook URL is invalid.
    """

    discord_webhook = None
    try:
        (webhook_id, token) = _parse_url(url)
        discord_webhook = discord.SyncWebhook.partial(webhook_id, token)
    except Exception as e:
        Logger.debug(f"{e}", {"exc_info": True})
    return discord_webhook


class Webhooker:

    def __init__(self, webhooks_json: dict) -> None:
        self.json_webhooks = webhooks_json
        self.discord_webhooks = dict()

        if len(self.json_webhooks['webhooks']) == 1 \
                and self.json_webhooks['webhooks'][0]['url'] == "https://discord.com/api/webhooks/RANDOM_STRING/RANDOM_STRING":
            Logger.log("Create an entry in 'webhooks.json' and enter the name into one or more 'subscriptions.json' entries to be notified when new files are downloaded.", {"tip": True})
            return

        if len(self.json_webhooks['webhooks']) > 0:
            Logger.log("Connecting to Discord webhooks...")

            for webhook in self.json_webhooks.get('webhooks', []):
                if webhook['url'] == "https://discord.com/api/webhooks/RANDOM_STRING/RANDOM_STRING":
                    continue
                if webhook['name'] == "" or webhook['url'] == "":
                    Logger.log("Webhook entries must have values for the 'name' and 'url' properties to connect to a webhook.", {"tip": True})

                try:
                    webhook_id, token = _parse_url(webhook['url'])
                    discord_webhook = discord.SyncWebhook.partial(webhook_id, token)
                    self.discord_webhooks[webhook['name']] = discord_webhook

                    Logger.log(f" - Connected to '{webhook['name']}' webhook.")
                except Exception as e:
                    Logger.log(f" - Error connecting to '{webhook['name']}' webhook.")
                    Logger.debug(f"{e}", {"exc_info": True})

    def get_json_webhook(self, name: str) -> dict | None:
        """
        Returns a webhook entry from the 'webhooks' dictionary.
        :param name: The name of the webhook.
        :return: The webhook entry dictionary. `None` if the webhook is not found.
        """

        for webhook in self.json_webhooks.get('webhooks'):
            if webhook.get('name') == name:
                return webhook
        return None

    def get_discord_webhook(self, name: str) -> discord.SyncWebhook | None:
        """
        Returns a Discord webhook object from the 'discord_webhooks' dictionary.
        :param name:
        :return: The Discord webhook object. `None` if the webhook is not found.
        """

        return self.discord_webhooks.get(name, None)

    def send_notification(self, webhook_name: str, torrent: dict, webhook: dict = None, url: str = None) -> None:
        """
        Sends a notification to a Discord webhook.
        :param webhook_name: The name of the webhook.
        :param torrent: A dictionary of a torrent entry.
        :param webhook: A webhook entry dictionary (Defaults to `None`).
        :param url: A Discord webhook URL (Defaults to `None`).
        :return: None
        """

        if not url or not webhook:
            webhook_json = self.get_json_webhook(webhook_name)
            discord_webhook = self.get_discord_webhook(webhook_name)
        else:
            webhook_json = webhook
            discord_webhook = create_webhook(url)

        if not webhook_json or not discord_webhook:
            Logger.log(f"Webhook Error: Cannot find '{webhook_name}' webhook.")
            return

        notification = discord.Embed()

        # Notification title
        title = webhook_json.get('notifications').get('title')
        notification.title = f"Downloading New Torrent: {torrent.get('title')}" if title == "" else _insert_tags(title, webhook_json.get('name'), torrent)

        # Notification description (no default value)
        if webhook_json.get('notifications').get('description') != "":
            notification.description = _insert_tags(webhook_json.get('notifications').get('description'), webhook_json.get('name'), torrent)

        # Notification hyperlink to Nyaa page
        notification.url = f"{torrent.get('id')}"

        # Notification 'show_' details
        notification = _apply_fields(webhook_json, notification, torrent)

        try:
            Logger.debug(f"Sending notification via '{webhook_name}' discord webhook...")
            discord_webhook.send(embed=notification)
            Logger.debug(f"Notification sent via '{webhook_name}' webhook.")
        except Exception as e:
            Logger.log(f"Webhook Error: Failed to send notification via '{webhook_name}' discord webhook.")
            Logger.debug(f"{e}", {"exc_info": True})
