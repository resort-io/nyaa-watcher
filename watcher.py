import os
import re
import logging
import feedparser

from datetime import datetime

log = logging.getLogger("watcher")


class WatcherError(Exception):
    pass


class Watcher:

    def __init__(self, watchlist: dict, history: dict) -> None:
        self.watchlist = watchlist
        self.history = history

    def get_history(self) -> dict:
        return self.history

    def get_watchlist(self) -> dict:
        return self.watchlist

    def add_to_history(self, torrent: dict) -> None:
        entry = {
            "torrent_title": torrent['title'],
            "date_downloaded": str(datetime.now()),
            "nyaa_page": torrent['id'],
            "nyaa_hash": torrent['nyaa_infohash']
        }
        self.history["history"].append(entry)

    def fetch_new_torrents(self, nyaa_rss: str) -> list:
        feed = feedparser.parse(nyaa_rss)

        new_torrents = []
        for torrent in feed.entries:
            title = torrent['title']
            hash = torrent['nyaa_infohash']

            if os.environ.get("LOG_RSS_ENTRIES", "true") == "true":
                log.debug(f"Checking: {title}")

            # Checking for title in watchlists
            for feed_entry in self.watchlist['feeds']:
                for watchlist_entry in feed_entry['watchlist']:
                    name = watchlist_entry["name"]
                    tags = watchlist_entry["tags"]
                    regexes = watchlist_entry["regex"]

                    # Webhooks
                    if "webhooks" in watchlist_entry and len(watchlist_entry["webhooks"]) > 0:
                        watchlist_webhooks = watchlist_entry["webhooks"]
                    else:
                        watchlist_webhooks = []

                    # Tags
                    if len(tags) == 0:
                        tag_match = "N/A"
                    else:
                        tag_match = False
                        for tag in tags:
                            if tag.lower() in title.lower():
                                tag_match = True
                                break

                    # RegEx
                    if len(regexes) == 0:
                        regex_match = "N/A"
                    else:
                        regex_match = False
                        for regex_pattern in regexes:
                            pattern = re.compile(regex_pattern)
                            if re.search(pattern, title) is not None:
                                regex_match = True
                                break

                    # History, if RegEx and a Tag match
                    hash_match = False
                    if tag_match is True and regex_match is True \
                            or tag_match == "N/A" and regex_match is True \
                            or tag_match is True and regex_match == "N/A":
                        for history_entry in self.history["history"]:
                            if history_entry["nyaa_hash"] == hash:
                                hash_match = True
                                break

                    if os.environ.get("LOG_RSS_ENTRIES", "true") == "true":
                        log.debug(f" - Watchlist: {name}")
                        log.debug(f" - Tags  (Match={tag_match}): {tags}")
                        log.debug(f" - RegEx (Match={regex_match}): {regexes}")
                        log.debug(f" - Hash  (Match={hash_match}): {hash}")

                    # Add to download list
                    if tag_match is True and regex_match is True and not hash_match \
                            or tag_match == "N/A" and regex_match is True and not hash_match \
                            or tag_match is True and regex_match == "N/A" and not hash_match:
                        torrent['webhooks'] = watchlist_webhooks
                        new_torrents.append(torrent)
                        if os.environ.get("LOG_RSS_ENTRIES", "true") == "true":
                            log.debug("New torrent. Added to download list.")
                            log.debug("")
                        break
                    if os.environ.get("LOG_RSS_ENTRIES", "true") == "true":
                        log.debug("")

        return new_torrents

    def fetch_all_feeds(self) -> list:
        torrents = []

        for feed_entry in self.watchlist['feeds']:
            nyaa_user = feed_entry['nyaa_rss'].replace("https://nyaa.si/?page=rss&u=", "")
            log.info(f" - Reading {nyaa_user}'s feed:")

            new_torrents = self.fetch_new_torrents(feed_entry['nyaa_rss'])
            log.info(f"   {len(new_torrents)} new torrents.")

            if len(new_torrents) > 0:
                for torrent in new_torrents:
                    log.info(f"   - {torrent['title']}")
                torrents += new_torrents

        return torrents
