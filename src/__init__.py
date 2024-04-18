import json
import logging
import os
import requests
import sched
import time
from config import Config
from dotenv import load_dotenv
from logger import Logger
from watcher import Watcher
from webhook import Webhook
from functions import download_torrent, fetch

load_dotenv()
log = logging.getLogger("main")


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    Logger.debug(f"Environment: {os.environ.get('ENV', 'PRODUCTION').upper()}")
    Logger.log("~~~ Nyaa Watcher ~~~")

    if not os.path.exists(os.environ.get("DOWNLOADS_DIR", "/downloads")):
        Logger.log("Map the '/downloads' directory to access downloaded files.", {"tip": True})

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

    Logger.log("Connecting to RSS...")
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
    Logger.debug(f"Connection successful. HTTPS Status Code: {str(response.status_code)}.")

    Logger.log("Done! Watcher started.")
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
