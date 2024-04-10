import os
import logging
import requests
import sched
import time
from env import Env
from dotenv import load_dotenv
from config import Config
from watcher import Watcher
from webhook import Webhook
from logger import Logger

load_dotenv()
env = Env()
log = logging.getLogger("main")


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


def fetch(scheduler: sched, watcher: Watcher, interval: int, webhook: Webhook) -> None:
    # Reading RSS feed
    Logger.log("Searching for matching torrents...", {"white_lines": "t"})
    torrents = watcher.get_new_torrents()

    # No new torrents
    if len(torrents) == 0:
        interval_string = Config.get_interval_string(interval)
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
            Logger.debug(f" - Downloading: {torrent['title']}...")
            download_status = download_torrent(torrent)

            # Success
            if download_status == "success":
                new_history_entries.append(torrent)
                Logger.debug(f" - Downloaded: {torrent['title']}")

                for webhook_name in torrent['webhooks']:
                    webhook.send_notification(webhook_name, torrent)

            # Error
            else:
                Logger.log(f" - Error downloading file. f{download_status}")
                errors += 1
            Logger.debug()

        Config.append_to_history(new_history_entries)
        watcher.append_to_history(new_history_entries)
        interval_string = Config.get_interval_string(interval)
        Logger.log(f"Done. Finished with {errors} error{'' if errors == 1 else 's'}.\nSearching for new torrents in {interval_string}.")

    # Schedule next check
    scheduler.enter(interval, 1, fetch, (scheduler, watcher, interval, webhook))


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=os.environ.get("LOG_LEVEL", "INFO"),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    Logger.log("~~~ Nyaa Watcher ~~~\nStarting watcher...")

    try:
        Config.verify_and_migrate()

        interval = Config.get_watcher_interval()

        rss = Config.get_nyaa_rss()
        watchlist = Config.get_watcher_watchlist()
        history = Config.get_watcher_history()
        watcher = Watcher(rss, watchlist, history)

        discord_webhooks = Config.get_discord_webhooks()
        webhook = Webhook(discord_webhooks)

        Logger.debug(f"INTERVAL: {interval} seconds.\n"
                     f"NYAA RSS: {rss}\n"
                     f"WATCHLIST: {len(watchlist['watchlist'])} entries.\n"
                     f"HISTORY: {len(history['history'])} entries.\n"
                     f"WEBHOOKS: {len(discord_webhooks['webhooks'])} entries.")
    except Exception as e:
        Logger.log(f"{e}\nWatcher exited.", {"white_lines": "b"})
        exit(-1)

    Logger.log("Attempting to reach RSS URL...")
    try:
        response = requests.get(rss, timeout=60)

        if response.status_code != 200:
            Logger.log(f"Connection Error: Could not read RSS URL; received HTTPS Status Code: {str(response.status_code)}. "
                       f"Add a valid Nyaa RSS URL to config.json and restart the server.\nWatcher exited.", {"white_lines": "b"})
            exit(-1)
    except Exception as e:
        Logger.log("Connection Error: Cannot connect to RSS URL. Your internet provider could be blocking requests to nyaa domains."
                   f"\n{e}\nWatcher exited.", {"exc_info": True, "white_lines": "b"})
        exit(-1)
    Logger.log("Success!\nWatcher started.")

    try:
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(1, 1, fetch, (scheduler, watcher, interval, webhook))
        scheduler.run()
    except KeyboardInterrupt:
        Logger.log("Watcher exited.", {"white_lines": "b"})
        exit(0)


if __name__ == "__main__":
    main()
