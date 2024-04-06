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
            time.sleep(0.1)  # Wait for file to finish
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


def update_history_file(watcher: Watcher) -> None:
    history = watcher.get_history()

    file_directory = os.environ.get("WATCHER_DIRECTORY", "") + "/history.json"
    file = open(file_directory, "w")
    file.write(json.dumps(history, indent=2))
    file.close()


def check_rss(scheduler: sched, watcher: Watcher, interval: int, webhook: Webhook) -> None:
    # Schedule next check
    scheduler.enter(interval, 1, check_rss, (scheduler, watcher, interval, webhook))

    # Reading torrents
    log.info("")
    log.info("Searching for matching torrents...")
    torrents = watcher.fetch_new_torrents()
    torrents = sort_torrents(torrents)
        
    interval_string = get_interval_string(interval)

    # No new torrents
    if len(torrents) == 0:
        log.info("No new torrents found.")
        log.info(f"Searching for matching torrents in {interval_string}.")
    # New torrents
    else:
        log.info("1 new torrent:") if len(torrents) == 1 \
            else log.info(f"{len(torrents)} new torrents:")

        # Display torrents
        for torrent in torrents:
            log.info(f" - {torrent['title']}")

        # Download torrents
        log.info("Downloading...")
        log.debug("")
        errors = 0
        for torrent in torrents:
            log.debug(f" - Downloading: {torrent['title']}")
            download_status = download_torrent(torrent)

            # Success
            if download_status == "success":
                watcher.add_to_history(torrent)
                log.debug(" - Success.")

                # Sending Discord notification to each webhook in watchlist
                if len(torrent['webhooks']) > 0:
                    for webhook_name in torrent['webhooks']:
                        webhook.send_notification(webhook_name, torrent)

            # Error
            else:
                log.debug(" - Error downloading file. " + download_status)
                errors += 1
            log.debug("")

        update_history_file(watcher)
        log.debug("Updated history.json.")

        log.info(f"Done. Finished with {errors} errors.")
        log.info(f"Searching for matching torrents in {interval_string}.")


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=os.environ.get("LOG_LEVEL", "INFO"),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log.info("~~~ Nyaa Watcher ~~~")
    log.info("Starting watcher...")

    try:
        config = Config()

        NYAA_RSS = config.get_nyaa_rss()
        log.debug(f"NYAA RSS: {NYAA_RSS}")

        WATCHER_INTERVAL = config.get_watcher_interval()
        log.debug(f"WATCHER INTERVAL: {WATCHER_INTERVAL} seconds.")

        WATCHER_WATCHLIST = config.get_watcher_watchlist()
        log.debug(f"WATCHER WATCHLIST: {len(WATCHER_WATCHLIST['watchlist'])} entries.")

        WATCHER_HISTORY = config.get_watcher_history()
        log.debug(f"WATCHER HISTORY: {len(WATCHER_HISTORY['history'])} entries.")

        watcher = Watcher(NYAA_RSS, WATCHER_WATCHLIST, WATCHER_HISTORY)

        WEBHOOKS = config.get_discord_webhooks()
        log.debug(f"DISCORD WEBHOOKS: {len(WEBHOOKS['webhooks'])} entries.")

        webhook = Webhook(WEBHOOKS)
    except Exception as e:
        log.info(e, exc_info=True)
        log.info("Watcher exited.")
        exit(-1)

    # Testing RSS URL
    log.info("Attempting to reach RSS URL...")
    try:
        response = requests.get(NYAA_RSS)
    except Exception as e:
        log.info("Connection Error: Cannot connect to RSS URL. Your internet provider could be blocking requests to nyaa domains.")
        log.info(e, exc_info=True)
        log.info("Watcher exited.")
        log.info("")
        exit(-1)

    if response.status_code != 200:
        log.info(f"Connection Error: Could not read RSS URL; received HTTPS Status Code: {str(response.status_code)}. "
                 "Add a valid Nyaa RSS URL to config.json and restart the server.")
        log.info("Watcher exited.")
        log.info("")
        exit(-1)

    log.info("Success!")
    log.info("Watcher started.")
    try:
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(1, 1, check_rss, (scheduler, watcher, WATCHER_INTERVAL, webhook))
        scheduler.run()
    except KeyboardInterrupt:
        log.info("Watcher exited.")
        log.info("")
        exit(0)


if __name__ == "__main__":
    main()
