import json
import logging
import os
import sched
import time
from config import Config
from dotenv import load_dotenv
from functions import fetch
from logger import Logger
from watcher import Watcher
from webhooker import Webhooker

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
        Logger.log("Map a local directory to the '/downloads' container directory to access downloaded files.", {"tip": True})

    try:
        Config.update_and_verify()

        interval = Config.get_interval()
        subscriptions = Config.get_subscriptions()
        history = Config.get_history()
        webhooks = Config.get_webhooks()

        watcher = Watcher(subscriptions, history)
        webhooker = Webhooker(webhooks)

        Logger.debug(
            f"INTERVAL: {interval} seconds.\n"
            f"SUBSCRIPTIONS: {len(subscriptions.get('subscriptions'))} entries.\n"
            f"HISTORY: {len(history.get('downloads'))} download(s) and {len(history.get('errors'))} error(s).\n"
            f"WEBHOOKS: {len(webhooks.get('webhooks'))} entries."
        )
        Logger.log(f"Done! Watcher started (v{Config.version}).")

        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(1, 1, fetch, (scheduler, watcher, interval, webhooker))
        scheduler.run()

    except KeyboardInterrupt:
        Logger.log("Watcher exited.", {"white_lines": "bt"})
        exit(0)
    except json.decoder.JSONDecodeError as e:
        line = e.doc.split("\n")[e.lineno - 1].replace("  ", "")
        message = "'" + e.msg + "'" if '.json' in e.msg else 'JSON'

        Logger.log(f"Parse Error: {message} syntax error found on line {e.lineno} at column {e.pos}.\n"
                   f"    {line}\nWatcher exited.", {"white_lines": "b"})
        Logger.debug(f"{e}", {"exc_info": True})
    except Exception as e:
        Logger.log(f"{e}\nWatcher exited.", {"white_lines": "b"})
        Logger.debug(f"{e}", {"exc_info": True})
    exit(1)


if __name__ == "__main__":
    main()
