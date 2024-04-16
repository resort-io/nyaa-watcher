import json
from datetime import datetime
import os
import logging
import requests
import sched
import time
from dotenv import load_dotenv
from config import Config
from watcher import Watcher
from webhook import Webhook
from logger import Logger

load_dotenv()
log = logging.getLogger("main")


def download_torrent(torrent: dict) -> dict:
    torrent_title = torrent.get('title') + ".torrent"
    torrent_url = torrent.get('link')

    file_path = os.environ.get("DOWNLOADS_DIR", "/downloads") + "/" + torrent_title
    try:
        response = requests.get(torrent_url)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            time.sleep(0.01)
        return {"status": response.status_code}
    except Exception as e:
        return {"status": 500, "message": str(e)}


def fetch(scheduler: sched, watcher: Watcher, interval: int, webhook: Webhook) -> None:
    Logger.log("Searching for matching torrents...", {"white_lines": "t"})
    torrents = watcher.fetch_new_torrents()

    # No new torrents
    if len(torrents) == 0:
        interval_string = Config.get_interval_string(interval)
        Logger.log(f"Found 0 new torrents.\nSearching for matching torrents in {interval_string}.")
    # New torrents
    else:
        Logger.log(f"Found {len(torrents)} new torrent{'' if len(torrents) == 1 else 's'}. Downloading...")
        successes = list()
        errors = list()

        for torrent in torrents:
            Logger.debug(f" - Downloading: {torrent.get('title')}...")
            download = download_torrent(torrent)
            torrent['download_datetime'] = str(datetime.now())

            if download.get('status') == 200:
                Logger.log(f" - Downloaded: {torrent.get('title')}")
                successes.append(torrent)

                for webhook_name in torrent.get('watcher_webhooks'):
                    webhook.send_notification(webhook_name, torrent)
            else:
                Logger.log(f" - Error: {torrent.get('title')} (HTTP Status Code: {download.get('status')}.")
                if 'message' in download:
                    Logger.debug(f" - {download.get('message')}")
                errors.append(torrent)
            Logger.debug()

        watcher.append_to_history(successes)
        Config.append_to_history(successes, errors)
        interval_string = Config.get_interval_string(interval)
        Logger.log(f"Done. Finished with {len(errors)} error{'' if len(errors) == 1 else 's'}.\nSearching for new torrents in {interval_string}.")

    # Schedule next check
    scheduler.enter(interval, 1, fetch, (scheduler, watcher, interval, webhook))


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    Logger.debug(f"Environment: {os.environ.get('ENV', 'PRODUCTION').upper()}")
    Logger.log("~~~ Nyaa Watcher ~~~")

    try:
        Config.update_and_verify()

        interval = Config.get_watcher_interval()

        rss = Config.get_nyaa_rss()
        watchlist = Config.get_watcher_watchlist()
        history = Config.get_watcher_history()
        watcher = Watcher(rss, watchlist, history)

        discord_webhooks = Config.get_discord_webhooks()
        webhook = Webhook(discord_webhooks)

        Logger.debug(f"INTERVAL: {interval} seconds.\n"
                     f"NYAA RSS: {rss}\n"
                     f"WATCHLIST: {len(watchlist.get('watchlist'))} entr{'y' if len(watchlist.get('watchlist')) == 1 else 'ies'}.\n"
                     f"HISTORY: {len(history.get('downloads'))} download(s) and {len(history.get('errors'))} error(s).\n"
                     f"WEBHOOKS: {len(webhook.get_json_webhooks().get('webhooks'))} entr{'y' if len(webhook.get_json_webhooks().get('webhooks')) == 1 else 'ies'}.")
    except json.decoder.JSONDecodeError as e:
        line = e.doc.split("\n")[e.lineno - 1].replace("  ", "")
        message = "'" + e.msg + "'" if '.json' in e.msg else 'JSON'
        Logger.log(f"Parse Error: {message} syntax error found on line {e.lineno} at column {e.pos}.\n"
                   f"    {line}\nWatcher exited.", {"white_lines": "b"})
        Logger.debug(f"{e}", {"exc_info": True})
        exit(-1)
    except Exception as e:
        Logger.log(f"{e}\nWatcher exited.", {"white_lines": "b"})
        Logger.debug(f"{e}", {"exc_info": True})
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
        Logger.log("Watcher exited.", {"white_lines": "bt"})
        exit(0)
    except Exception as e:
        Logger.log(f"{e}\nWatcher exited.", {"white_lines": "bt"})
        Logger.debug(f"{e}", {"exc_info": True})
        exit(-1)


if __name__ == "__main__":
    main()
