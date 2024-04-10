import discord
import re
from logger import Logger


class WebhookError(Exception):
    pass


def _apply_fields(webhook_json: dict, notification: discord.Embed, torrent: dict) -> discord.Embed:
    for i in range(1, 7):
        if webhook_json['notifications']['show_downloads'] == i:
            notification.add_field(name="Downloads", value=torrent['nyaa_downloads'])
        elif webhook_json['notifications']['show_seeders'] == i:
            notification.add_field(name="Seeders", value=torrent['nyaa_seeders'])
        elif webhook_json['notifications']['show_leechers'] == i:
            notification.add_field(name="Leechers", value=torrent['nyaa_leechers'])
        elif webhook_json['notifications']['show_published'] == i:
            notification.add_field(name="Published", value=re.sub(r":\d\d -0000", "", torrent['published']))
        elif webhook_json['notifications']['show_category'] == i:
            notification.add_field(name="Category", value=torrent['nyaa_category'])
        elif webhook_json['notifications']['show_size'] == i:
            notification.add_field(name="Size", value=torrent['nyaa_size'])
    return notification


def _parse_url(url: str) -> list:
    return (
        url.replace("https://discord.com/api/webhooks/", "")
        .replace("https://discordapp.com/api/webhooks/", "")
        .split("/")
    )


def _insert_tags(string: str, webhook_name: str, torrent: dict) -> str:
    string = string.replace("$webhook_name", webhook_name) \
        .replace("$title", torrent['title']) \
        .replace("$downloads", torrent['nyaa_downloads']) \
        .replace("$seeders", torrent['nyaa_seeders']) \
        .replace("$leechers", torrent['nyaa_leechers']) \
        .replace("$size", torrent['nyaa_size']) \
        .replace("$published", re.sub(r":\d\d -0000", "", torrent['published'])) \
        .replace("$category", torrent['nyaa_downloads'])
    return string


class Webhook:

    def __init__(self, webhooks: dict) -> None:
        self.json_webhooks = webhooks
        self.discord_webhooks = dict()

        if len(self.json_webhooks['webhooks']) > 0:
            Logger.log("Connecting to Discord webhooks...")

            connected = 0
            for webhook in self.json_webhooks['webhooks']:
                if webhook['name'] == "" or webhook['url'] == "":
                    raise WebhookError("Webhook entries must have a name and URL.")

                if webhook['url'] == "https://discord.com/api/webhooks/RANDOM_STRING/RANDOM_STRING":
                    continue

                Logger.log(f" - Connected to '{webhook['name']}' webhook.")
                id, token = _parse_url(webhook['url'])

                try:
                    discord_webhook = discord.SyncWebhook.partial(id, token)
                    self.discord_webhooks[webhook['name']] = discord_webhook
                    connected += 1
                except Exception as e:
                    Logger.log(f" - Error connecting to '{webhook['name']}' webhook.")
                    Logger.debug(f"{e}", {"exc_info": True})

            Logger.log(f"Connected to 1 Discord webhook.") if connected == 1 \
                else Logger.log(f"Connected to {connected} Discord webhooks.")

    def get_json_webhooks(self) -> dict:
        return self.json_webhooks

    def get_json_webhook(self, name: str) -> dict | None:
        for webhook in self.json_webhooks['webhooks']:
            if webhook['name'] == name:
                return webhook
        return None

    def get_discord_webhook(self, name: str) -> discord.SyncWebhook | None:
        return self.discord_webhooks.get(name)

    def send_notification(self, webhook_name: str, torrent: dict) -> None:
        webhook_json = self.get_json_webhook(webhook_name)
        discord_webhook = self.get_discord_webhook(webhook_name)
        if not webhook_json or not discord_webhook:
            Logger.log(f"Webhook Error: Cannot find '{webhook_name}' webhook.")
            return

        notification = discord.Embed()

        # Notification Title and Description
        title = webhook_json['notifications']['title']
        notification.title = f"Downloading New Torrent: {torrent.get('title')}" if title == "" else _insert_tags(title, webhook_json['name'], torrent)

        # Notification Title and Description
        if webhook_json['notifications']['description'] != "":
            notification.description = _insert_tags(webhook_json['notifications']['description'], webhook_json['name'], torrent)

        # Notification 'show_' Details
        notification = _apply_fields(webhook_json, notification, torrent)

        # Notification Nyaa URL
        notification.url = f"{torrent['id']}"

        try:
            Logger.debug(f"Sending notification to '{webhook_name}' discord webhook...")
            discord_webhook.send(embed=notification)
            Logger.debug("Notification sent.")
        except Exception as e:
            Logger.log(f"Webhook Error: Failed to send notification to '{webhook_name}' discord webhook.")
            Logger.debug(f"{e}", {"exc_info": True})
