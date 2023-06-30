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

load_dotenv()
log = logging.getLogger("main")
config = Config()


def download_torrent(torrent: dict) -> str:
    torrent_title = torrent['title'] + ".torrent"
    torrent_url = torrent['link']

    file_path = os.path.join(os.environ.get("WATCH_DIRECTORY", "/watch"), torrent_title)
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

    file_directory = os.environ.get("WATCHER_DIRECTORY", "/watcher") + "/history.json"
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

    if float(interval / 60) % 1 == 0:
        minutes = "%.0f" % float(interval / 60)
    elif (float(interval / 60) * 10) % 1 == 0:
        minutes = "%.1f" % float(interval / 60)
    else:
        minutes = "%.2f" % float(interval / 60)

    # No new torrents
    if len(torrents) == 0:
        log.info("No new torrents found.")
        if interval < 60:
            log.info(f"Searching for matching torrents in 1 second.") if interval == 1 \
                else log.info(f"Searching for matching torrents in {interval} seconds.")
        else:
            log.info("Searching for matching torrents in 1 minute.") if interval == 60 \
                else log.info(f"Searching for matching torrents in {minutes} minutes.")
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
        if interval < 60:
            log.info(f"Searching for matching torrents in 1 second.") if interval == 1 \
                else log.info(f"Searching for matching torrents in {interval} seconds.")
        else:
            log.info("Searching for matching torrents in 1 minute.") if interval == 60 \
                else log.info(f"Searching for matching torrents in {minutes} minutes.")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=os.environ.get("LOG_LEVEL", "INFO"),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log.info("~~~ Nyaa Watcher ~~~")
    log.info("Version: 1.1.0")
    log.info("Starting server...")

    try:
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
        log.info(e)
        log.info("Server exited.")
        exit(-1)

    # Verifying Watchlist
    if watcher.watchlist_is_empty():
        log.info("Watchlist Error: No watchlist entries found. Add an entry including a title with tag(s) and/or "
                 "regex(es) to watchlist.json and restart the server.")
        log.info("Server exited.")
        log.info("")
        exit(-1)
    if not watcher.watchlist_is_valid():
        log.info("Watchlist Error: One or more watchlist entries does not have a tag or regex. Add the tag or regex "
                 "to the entry/entries in watchlist.json and restart the server.")
        log.info("Server exited.")
        log.info("")
        exit(-1)

    # Verifying Webhooks
    try:
        webhook.webhooks_are_valid()
    except Exception as e:
        log.info(e)
        log.info("Server exited.")
        log.info("")
        exit(-1)

    # Verifying RSS URL
    if watcher.get_rss() == "https://nyaa.si/?page=rss&u=NYAA_USERNAME" \
            or watcher.get_rss() == "":
        log.info("Config Error: No Nyaa RSS found. Add a Nyaa RSS URL to config.json and restart the server.")
        log.info("Server exited.")
        log.info("")
        exit(-1)

    log.info("Attempting to reach RSS URL...")
    try:
        response = requests.get(NYAA_RSS)
    except Exception as e:
        log.info("Connection Error: Cannot connect to RSS URL. Your internet provider may be blocking the server.")
        log.info(e, exc_info=True)
        log.info("Server exited.")
        log.info("")
        exit(-1)

    if response.status_code == 200:
        log.info("Success. HTTPS Status Code: 200.")
    else:
        log.info(f"Connection Error: Could not read RSS URL; received HTTPS Status Code: {str(response.status_code)}. "
                 "Add a valid Nyaa RSS URL to config.json and restart the server.")
        log.info("Server exited.")
        log.info("")
        exit(-1)

    log.info("Server started.")
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(1, 1, check_rss, (scheduler, watcher, WATCHER_INTERVAL, webhook))
    scheduler.run()
