import logging
import discord
import re

from typing import Any

log = logging.getLogger("webhook")


class WebhookError(Exception):
    pass


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
        self.webhooks = webhooks
        # Two lists to maintain index continuity
        self.webhook_names = list()
        self.discord_webhooks = list()

        if len(self.webhooks['webhooks']) > 0:
            log.info("Connecting to Discord webhooks...")

            connected = 0
            for webhook in self.webhooks['webhooks']:
                if webhook['name'] == "" or webhook['url'] == "":
                    raise WebhookError("Webhook Error: Webhook entries must have a name and URL.")

                if webhook['url'] == "https://discord.com/api/webhooks/RANDOM_STRING/RANDOM_STRING":
                    continue

                log.debug(f" - {webhook['name']} ({webhook['url']})")
                id, token = _parse_url(webhook['url'])
                try:
                    discord_webhook = discord.SyncWebhook.partial(id, token)
                    self.webhook_names.append(webhook['name'])
                    self.discord_webhooks.append(discord_webhook)
                    connected += 1
                except Exception as e:
                    log.info(f"Webhook Error: Cannot connect to '{webhook['name']}' webhook at {webhook['url']}.")
                    log.debug(e, exc_info=True)

            log.info(f"Connected to 1 Discord webhook.") if connected == 1 \
                else log.info(f"Connected to {connected} Discord webhooks.")

    def get_webhooks(self) -> dict:
        return self.webhooks

    def get_webhook_by_name(self, name: str) -> bool | Any:
        for webhook in self.webhooks['webhooks']:
            if webhook['name'].lower() == name.lower():
                return webhook
        return False

    def get_discord_webhook_by_name(self, name: str) -> bool | Any:
        try:
            index = self.webhook_names.index(name)
            return self.discord_webhooks[index]
        except Exception as e:
            return False

    def send_notification(self, webhook_name: str, torrent: dict) -> None:
        # Finding webhook dict
        webhook_json = self.get_webhook_by_name(webhook_name)
        if webhook_json is False:
            log.info(f"Watchlist Error: Cannot find '{webhook_name}' in webhooks.json.")
            return

        notification = discord.Embed()

        # Title
        if webhook_json['notifications']['title'] != "":
            notification.title = _insert_tags(webhook_json['notifications']['title'],
                                              webhook_json['name'],
                                              torrent)
        else:
            notification.title = f"Downloading New Torrent: {torrent['title']}"

        # Description
        if webhook_json['notifications']['description'] != "":
            notification.description = _insert_tags(webhook_json['notifications']['description'],
                                                    webhook_json['name'],
                                                    torrent)

        # Custom Notification Details
        i = 1
        while i <= 6:
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
            i += 1

        # Nyaa Page URL
        notification.url = f"{torrent['id']}"

        # Send notification
        log.debug(f"Sending Discord notification to webhook: {webhook_name}...")
        discord_webhook = self.get_discord_webhook_by_name(webhook_name)
        if discord_webhook is False:
            log.info(f"Webhook Error: Cannot find '{webhook_name}' in webhooks.json.")
        else:
            try:
                discord_webhook.send(embed=notification)
                log.debug("Done.")
            except Exception as e:
                log.info(f"Webhook Error: Failed to send notification to '{webhook_name}' webhook.")
                log.debug(e)
