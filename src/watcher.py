import feedparser
import os
import re
from logger import Logger


def _sort_torrents(torrents: list) -> list:
    torrent_titles = [(torrent['title'], torrent) for torrent in torrents]
    torrent_titles.sort()
    return [pair[1] for pair in torrent_titles]


class Watcher:

    def __init__(self, rss: str, watchlist_json: dict, history_json: dict, previous_hash: str = None) -> None:
        self.rss = rss
        self.watchlist = watchlist_json
        self.history = history_json
        self.previous_hash = previous_hash

    def append_to_history(self, torrents: list) -> None:
        for torrent in torrents:
            self.history.get('downloads').append({
                "torrent_title": torrent.get('title'),
                "date_downloaded": torrent.get('download_datetime'),
                "nyaa_page": torrent.get('id'),
                "nyaa_hash": torrent.get('nyaa_infohash')
            })

    def get_history(self) -> dict:
        return self.history

    def get_watchlist(self) -> dict:
        return self.watchlist

    def get_rss(self) -> str:
        return self.rss

    def fetch_new_torrents(self, rss: str = None) -> list:
        log_entries = os.environ.get("LOG_RSS_ENTRIES", "false").lower() == "true"

        if rss is None:
            rss = self.rss

        feed = feedparser.parse(rss)
        queue = []
        for torrent in feed.entries:
            title = torrent.get('title')
            torrent_hash = torrent.get('nyaa_infohash')

            # Check if the following torrents have already been fetched
            if torrent_hash == self.previous_hash:
                break

            for watchlist_entry in self.watchlist.get("watchlist"):
                # Checking Tags
                tags = watchlist_entry.get("tags")
                tag_match = None
                for tag in tags:
                    tag_match = False
                    if tag.lower() in title.lower():
                        tag_match = True
                        break

                # Checking RegEx
                regexes = watchlist_entry.get("regex")

                regex_match = None
                for regex_pattern in regexes:
                    regex_match = False
                    pattern = re.compile(regex_pattern)
                    if re.search(pattern, title):
                        regex_match = True
                        break

                # Checking if torrent already downloaded
                hash_match = False
                if tag_match is True and regex_match is True \
                        or tag_match is None and regex_match is True \
                        or tag_match is True and regex_match is None:
                    history_entry = [(entry['nyaa_hash'], entry) for entry in self.history.get("downloads") if entry.get('nyaa_hash') == torrent_hash]
                    hash_match = len(history_entry) > 0

                if log_entries:
                    Logger.debug(f"RSS Entry: {title}\n"
                                 f" - Watchlist: {watchlist_entry.get('name')}\n"
                                 f" - Tags  (Match={tag_match}): {tags}\n"
                                 f" - RegEx (Match={regex_match}): {regexes}\n"
                                 f" - Hash  (Match={hash_match}): {torrent_hash}")

                # Add to queue
                if (tag_match is True and regex_match is True
                        or tag_match is None and regex_match is True
                        or tag_match is True and regex_match is None) and not hash_match:
                    torrent['watcher_webhooks'] = watchlist_entry.get("webhooks", [])  # Attach webhook(s) to torrent
                    queue.append(torrent)

                    if log_entries:
                        Logger.debug("New torrent. Added to download list.", {"white_lines": "b"})
                    break

                if log_entries:
                    Logger.debug()

        self.previous_hash = feed.entries[0].get('nyaa_infohash')
        return _sort_torrents(queue)
