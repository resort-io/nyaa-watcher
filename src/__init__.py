import json
import os
import logging
import requests
import sched
import time
from dotenv import load_dotenv
from config import Config
from watcher import Watcher
from webhook import Webhook
from math import floor
from logger import Logger

load_dotenv()
log = logging.getLogger("main")


def get_interval_string(interval: int) -> str:
    days = floor(interval / 86400)
    if days > 0:
        interval -= floor(days * 86400)

    hours = floor(interval / 3600)
    if hours > 0:
        interval -= floor(hours * 3600)

    minutes = floor(interval / 60)
    if minutes > 0:
        interval -= floor(minutes * 60)

    seconds = interval

    array = [days, hours, minutes, seconds]

    # Find last non-zero index
    last_index = -1
    i = 0
    while i <= 3:
        if array[i] > 0:
            last_index = i
        i += 1

    # Number of units to display
    units = 0
    for value in array:
        if value > 0:
            units += 1

    # Build string
    if units == 1:
        if days > 0:
            return f"{days} day" if days == 1 else f"{days} days"
        elif hours > 0:
            return f"{hours} hour" if hours == 1 else f"{hours} hours"
        elif minutes > 0:
            return f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"
        else:
            return f"{seconds} second" if seconds == 1 else f"{seconds} seconds"
    else:
        string = ""

        # Days
        if array[0] > 0:
            string += f"{days} day" if days == 1 else f"{days} days"
            if last_index != 0:
                string += ", "
            units -= 1
        # Hours
        if array[1] > 0:
            if last_index == 1 and units == 1:
                string += f"and {hours} hour" if hours == 1 else f"and {hours} hours"
            else:
                string += f"{hours} hour" if hours == 1 else f"{hours} hours"
                if last_index != 1:
                    string += ", "
                units -= 1
        # Minutes
        if array[2] > 0:
            if last_index == 2 and units == 1:
                string += f"and {minutes} minute" if minutes == 1 else f"and {minutes} minutes"
            else:
                string += f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"
                if last_index != 2:
                    string += ", "
                units -= 1
        # Seconds
        if array[3] > 0:
            string += f"and {seconds} second" if seconds == 1 else f"and {seconds} seconds"

        return string


def download_torrent(torrent: dict) -> str:
    torrent_title = torrent['title'] + ".torrent"
    torrent_url = torrent['link']

    file_path = os.path.join(os.environ.get("WATCH_DIRECTORY", "../watch"), torrent_title)
    try:
        response = requests.get(torrent_url)
        # Success
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            time.sleep(0.1)
            return "success"
        # Failure
        else:
            return f"HTTP Status Code: {str(response.status_code)}."
    except Exception as e:
        return "Download Error: " + str(e)


def sort_torrents(torrents: list) -> list:
    torrent_titles = [(torrent['title'], torrent) for torrent in torrents]
    torrent_titles.sort()

    sorted_list = [pair[1] for pair in torrent_titles]
    return sorted_list


def check_rss(scheduler: sched, watcher: Watcher, interval: int, webhook: Webhook, config: Config) -> None:
    # Reading RSS feed
    Logger.log("Searching for matching torrents...", {"white_lines": "t"})
    torrents = watcher.fetch_new_torrents()
    torrents = sort_torrents(torrents)

    # No new torrents
    if len(torrents) == 0:
        interval_string = get_interval_string(interval)
        Logger.log(f"No new torrents found.\nSearching for matching torrents in {interval_string}.")
    # New torrents
    else:
        Logger.log(f"{len(torrents)} new torrent{'' if len(torrents) == 1 else 's'}:")
        for torrent in torrents:
            Logger.log(f" - {torrent['title']}")
        Logger.log("Downloading...", {"white_lines": "b"})

        new_history_entries = list()
        errors = 0
        for torrent in torrents:
            Logger.log(f" - Downloading: {torrent['title']}")
            download_status = download_torrent(torrent)

            # Success
            if download_status == "success":
                # watcher.add_to_history(torrent)
                new_history_entries.append(torrent)
                Logger.debug(" - Success.")

                for webhook_name in torrent['webhooks']:
                    webhook.send_notification(webhook_name, torrent)

            # Error
            else:
                Logger.log(f" - Error downloading file. f{download_status}")
                errors += 1
            Logger.debug()

        Config.append_to_history(new_history_entries)
        interval_string = get_interval_string(interval)
        Logger.log(f"Done. Finished with {errors} error{'' if errors == 1 else 's'}.\nSearching for matching torrents in {interval_string}.")

    # Schedule next check
    scheduler.enter(interval, 1, check_rss, (scheduler, watcher, interval, webhook, config))


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=os.environ.get("LOG_LEVEL", "INFO"),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    Logger.log("~~~ Nyaa Watcher ~~~\nStarting watcher...")

    try:
        config = Config()

        NYAA_RSS = config.get_nyaa_rss()
        Logger.debug(f"NYAA RSS: {NYAA_RSS}")

        WATCHER_INTERVAL = config.get_watcher_interval()
        Logger.debug(f"WATCHER INTERVAL: {WATCHER_INTERVAL} seconds.")

        WATCHER_WATCHLIST = config.get_watcher_watchlist()
        Logger.debug(f"WATCHER WATCHLIST: {len(WATCHER_WATCHLIST['watchlist'])} entries.")

        WATCHER_HISTORY = config.get_watcher_history()
        Logger.debug(f"WATCHER HISTORY: {len(WATCHER_HISTORY['history'])} entries.")

        watcher = Watcher(NYAA_RSS, WATCHER_WATCHLIST, WATCHER_HISTORY)

        WEBHOOKS = config.get_discord_webhooks()
        Logger.debug(f"DISCORD WEBHOOKS: {len(WEBHOOKS['webhooks'])} entries.")

        webhook = Webhook(WEBHOOKS)
    except Exception as e:
        Logger.log(f"{e}\nWatcher exited.", {"white_lines": "b"})
        exit(-1)

    # Testing RSS URL
    Logger.log("Attempting to reach RSS URL...")
    try:
        response = requests.get(NYAA_RSS)
    except Exception as e:
        Logger.log("Connection Error: Cannot connect to RSS URL. Your internet provider could be blocking requests to nyaa domains."
                   f"\n{e}\nWatcher exited.", {"exc_info": True, "white_lines": "b"})
        exit(-1)

    if response.status_code != 200:
        Logger.log(f"Connection Error: Could not read RSS URL; received HTTPS Status Code: {str(response.status_code)}. "
                   f"Add a valid Nyaa RSS URL to config.json and restart the server.\nWatcher exited.", {"white_lines": "b"})
        exit(-1)

    Logger.log("Success!\nWatcher started.")
    try:
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(1, 1, check_rss, (scheduler, watcher, WATCHER_INTERVAL, webhook, config))
        scheduler.run()
    except KeyboardInterrupt:
        Logger.log("Watcher exited.", {"white_lines": "b"})
        exit(0)


if __name__ == "__main__":
    main()
