import json
import os
import logging
import requests
import sched
import time

from dotenv import load_dotenv
from config import Config
from watcher import Watcher

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
            return "HTTP Status Code: " + str(response.status_code) + "."
    except Exception as e:
        return "Unexpected error: " + str(e)


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


def check_rss(scheduler: sched, watcher: Watcher, interval: int) -> None:
    # Schedule next check
    scheduler.enter(interval, 1, check_rss, (scheduler, watcher, interval))

    # Reading torrents
    log.info("")
    log.info("Searching for matching torrents...")
    torrents = watcher.fetch_new_torrents()
    torrents = sort_torrents(torrents)

    # No new torrents
    if len(torrents) == 0:
        log.info("No new torrents found.")
        log.info("Searching for matching torrents in %.2f minutes" % float(interval / 60))
    # New torrents
    else:
        log.info(f"{len(torrents)} new torrents:")

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
            # Error
            else:
                log.debug(" - Error downloading file. " + download_status)
                errors += 1
            log.debug("")

        update_history_file(watcher)
        log.debug("Updated history.json.")

        log.info(f"Done. Finished with {errors} errors.")
        log.info("Searching for matching torrents in %.2f minutes." % float(interval / 60))


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=os.environ.get("LOG_LEVEL", "INFO"),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log.info("~~~ Nyaa Watcher ~~~")

    try:
        NYAA_RSS = config.get_nyaa_rss()
        log.debug(f"NYAA_RSS: {NYAA_RSS}")

        WATCHER_WATCHLIST = config.get_watcher_watchlist()
        log.debug(f"WATCHER_WATCHLIST: {len(WATCHER_WATCHLIST['watchlist'])} entries")

        WATCHER_HISTORY = config.get_watcher_history()
        log.debug(f"WATCHER_HISTORY: {len(WATCHER_HISTORY['history'])} entries")

        WATCHER_INTERVAL = config.get_watcher_interval()
        log.debug(f"WATCHER_INTERVAL: {WATCHER_INTERVAL} seconds")

        watcher = Watcher(NYAA_RSS, WATCHER_WATCHLIST, WATCHER_HISTORY)

        # Verifying Watchlist
        if watcher.watchlist_is_empty():
            log.info("No watchlist entries found. Add an entry including a title with tag(s) or regex(es) to "
                     "watchlist.json and restart the server.")
            log.info("Server exited.")
            log.info("")
            exit(-1)
        if not watcher.watchlist_is_valid():
            log.info("One or more watchlist entries does not have a tag or regex. Add the tag or regex to the "
                     "entry/entries in watchlist.json and restart the server.")
            log.info("Server exited.")
            log.info("")
            exit(-1)

        # Verifying RSS URL
        if watcher.get_rss() == "https://nyaa.si/?page=rss&u=NYAA_USERNAME" \
                or watcher.get_rss() == "":
            log.info("No Nyaa RSS found. Add a Nyaa RSS URL to config.json and restart the server.")
            log.info("Server exited.")
            log.info("")
            exit(-1)
        response = requests.get(NYAA_RSS)
        if response.status_code != 200:
            log.info("Could not read RSS URL. Add a valid Nyaa RSS URL to config.json and restart the server.")
            log.info("Server exited.")
            log.info("")
            exit(-1)

        log.info("Watcher started.")
    except Exception as e:
        log.info(e, exc_info=True)
        exit(-1)

    log.info("Server started.")

    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(1, 1, check_rss, (scheduler, watcher, WATCHER_INTERVAL))
    scheduler.run()
