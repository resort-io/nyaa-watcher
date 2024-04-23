import feedparser
import os
import re
from logger import Logger
from config import Config


def _sort_torrents(torrents: list) -> list:
    torrent_titles = [(torrent['title'], torrent) for torrent in torrents]
    torrent_titles.sort()
    return [pair[1] for pair in torrent_titles]


class Watcher:

    def __init__(self, subscriptions_json: dict, history_json: dict) -> None:
        self.subscriptions = subscriptions_json
        self.history = history_json

    def append_to_history(self, torrents: list) -> None:
        for torrent in torrents:
            self.history.get('downloads').append({
                "uploader": torrent.get('uploader'),
                "torrent_title": torrent.get('title'),
                "date_downloaded": torrent.get('download_datetime'),
                "nyaa_page": torrent.get('id'),
                "nyaa_hash": torrent.get('nyaa_infohash')
            })

    def fetch_feed(self, rss: str, watchlist: dict, sub_name: str = None, prev_hash: str = None) -> list:
        log_entries = os.environ.get("LOG_RSS_ENTRIES", "false").lower() == "true"

        feed = feedparser.parse(rss)
        if len(feed.entries) == 0:
            Logger.log(f"Cannot retrieve entries from {rss}.")
            return []

        queue = []
        for torrent in feed.entries:
            title = torrent.get('title')
            torrent_hash = torrent.get('nyaa_infohash')

            if log_entries:
                Logger.debug(f"Torrent: {title}")

            # Check if the following torrents have already been fetched
            if torrent_hash == prev_hash:
                break

            for watchlist_entry in watchlist:
                # Checking Tags
                tags = watchlist_entry.get("tags", [])
                tag_match = None
                for tag in tags:
                    tag_match = False
                    if tag.lower() in title.lower():
                        tag_match = True
                        break

                # Checking RegEx
                regexes = watchlist_entry.get("regex", [])
                regex_match = None
                for regex_pattern in regexes:
                    regex_match = False
                    pattern = re.compile(regex_pattern)
                    if re.search(pattern, title):
                        regex_match = True
                        break

                # Checking Hash
                hash_match = False
                if tag_match and regex_match or tag_match is None and regex_match or tag_match and regex_match is None:
                    history_entry = [(entry['nyaa_hash'], entry) for entry in self.history.get("downloads") if entry.get('nyaa_hash') == torrent_hash]
                    history_entry = history_entry if len(history_entry) > 0 else [(entry['nyaa_hash'], entry) for entry in self.history.get("errors") if entry.get('nyaa_hash') == torrent_hash]
                    hash_match = len(history_entry) > 0

                if log_entries:
                    Logger.debug(
                        f"Watchlist: {watchlist_entry.get('name')}\n"
                        f" - Tags  (Match={tag_match}): {tags}\n"
                        f" - RegEx (Match={regex_match}): {regexes}\n"
                        f" - Hash  (Match={hash_match}): {torrent_hash}"
                    )
                    if watchlist_entry == watchlist[-1]:
                        Logger.debug()

                # Add to queue if not already downloaded
                if (tag_match and regex_match or tag_match is None and regex_match or tag_match and regex_match is None) and not hash_match:
                    torrent['watcher_webhooks'] = watchlist_entry.get("webhooks", [])  # Attach webhook(s) to torrent
                    torrent['uploader'] = sub_name
                    queue.append(torrent)

                    if log_entries:
                        Logger.debug("Torrent added to download list.")
                    break

        if sub_name:
            Config.set_previous_hash(sub_name, feed.entries[0].get('nyaa_infohash', ""))
        return _sort_torrents(queue)

    def fetch_all_feeds(self) -> list:
        queue = []
        Logger.log()
        for sub in self.subscriptions.get("subscriptions"):
            Logger.log(f"Searching for new uploads from '{sub.get('username')}'...")
            queue += self.fetch_feed(sub.get('rss'), sub.get('watchlist'), sub.get('username'), sub.get('previous_hash'))
        return queue
