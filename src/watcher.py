import feedparser
import os
import re
from logger import Logger


def _sort_torrents(torrents: list) -> list:
    torrent_titles = [(torrent['title'], torrent) for torrent in torrents]
    torrent_titles.sort()
    return [pair[1] for pair in torrent_titles]


class Watcher:

    def __init__(self, rss: str, watchlist: dict, history: dict) -> None:
        self.rss = rss
        self.watchlist = watchlist
        self.history = history
        self.previous_hash = None

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

    def fetch_new_torrents(self) -> list:
        feed = feedparser.parse(self.rss)
        show_entries = os.environ.get("SHOW_RSS_ENTRIES", "false").lower() == "true"

        queue = []
        for torrent in feed.entries:
            title = torrent.get('title')
            torrent_hash = torrent.get('nyaa_infohash')

            # Check if the next torrents have already been checked in a previous fetch
            if torrent_hash == self.previous_hash:
                break

            if show_entries:
                Logger.debug(f"Checking: {title}")

            # Check if user is watching this title
            for watchlist_entry in self.watchlist.get("watchlist"):
                name = watchlist_entry.get("name")
                tags = watchlist_entry.get("tags")
                regexes = watchlist_entry.get("regex")

                # Searching for Tags and RegEx
                regex_match = tag_match = None
                for tag in tags:
                    tag_match = False
                    if tag.lower() in title.lower():
                        tag_match = True
                        break
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

                if show_entries:
                    Logger.debug(f" - Watchlist: {name}\n"
                                 f" - Tags  (Match={tag_match}): {tags}\n"
                                 f" - RegEx (Match={regex_match}): {regexes}\n"
                                 f" - Hash  (Match={hash_match}): {torrent_hash}")

                # Add to queue
                if (tag_match is True and regex_match is True
                        or tag_match is None and regex_match is True
                        or tag_match is True and regex_match is None) and not hash_match:
                    torrent['watcher_webhooks'] = watchlist_entry.get("webhooks", [])
                    queue.append(torrent)

                    if show_entries:
                        Logger.debug("New torrent. Added to download list.", {"white_lines": "b"})
                    break

                if show_entries:
                    Logger.debug()

        self.previous_hash = feed.entries[0].get('nyaa_infohash')
        return _sort_torrents(queue)
