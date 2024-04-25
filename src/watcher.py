import feedparser
import os
import re
from logger import Logger
from config import Config


def _sort_torrents(torrents: list) -> list:
    """
    Sorts a list of torrents based on their titles.
    :param torrents: A list of dictionaries, each representing an RSS torrent entry.
    :return: A list of sorted torrent dictionaries, ordered by their 'title' key in ascending order.
    """
    torrent_titles = [(torrent['title'], torrent) for torrent in torrents]
    torrent_titles.sort()
    return [pair[1] for pair in torrent_titles]


class Watcher:

    def __init__(self, subscriptions_json: dict, history_json: dict) -> None:
        self.subscriptions = subscriptions_json
        self.history = history_json

    def append_to_history(self, torrents: list) -> None:
        """
        Appends a list of torrents to the history.
        :param torrents: A list of dictionaries, each representing a torrent. Each dictionary must have the following keys:
                'uploader': The name of the uploader.
                'title': The title of the torrent.
                'download_datetime': The date and time when the torrent was downloaded.
                'id': The URL of the torrent.
                'nyaa_infohash': The hash of the torrent given by Nyaa.
        :return: None
        """
        for torrent in torrents:
            self.history.get('downloads').append({
                "uploader": torrent.get('uploader'),
                "torrent_title": torrent.get('title'),
                "date_downloaded": torrent.get('download_datetime'),
                "nyaa_page": torrent.get('id'),
                "nyaa_hash": torrent.get('nyaa_infohash')
            })

    def fetch_feed(self, rss: str, watchlist: dict, sub_name: str = None, prev_hash: str = None) -> list:
        """
        Fetches an RSS feed and filters the torrents based on the watchlist.
        :param rss: The URL of the RSS feed.
        :param watchlist: A dictionary containing the watchlist entries.
        :param sub_name: The name of the subscription (Defaults to None).
        :param prev_hash: The last torrent hash of the previous fetch (Defaults to None).
        :return: A list of dictionaries, each representing a torrents from a given subscription to be downloaded.
        """
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
                tag_match = regex_match = ex_regex_match = hash_match = False

                # Checking tags
                tags = watchlist_entry.get("tags", [])
                for tag in tags:
                    if tag.lower() in title.lower():
                        tag_match = True
                        break

                # Checking regex
                regexes = watchlist_entry.get("regex", [])
                for regex_pattern in regexes:
                    pattern = re.compile(regex_pattern)
                    if re.search(pattern, title):
                        regex_match = True
                        break

                # Checking excluded regex
                ex_regexes = watchlist_entry.get("exclude_regex", [])
                for regex_pattern in regexes:
                    pattern = re.compile(regex_pattern)
                    if re.search(pattern, title):
                        ex_regex_match = True
                        break

                match = tag_match and regex_match or len(tags) == 0 and regex_match or tag_match and len(regexes) == 0

                # Checking hash in successful downloads
                if match:
                    history_entry = [(entry['nyaa_hash'], entry) for entry in self.history.get("downloads") if entry.get('nyaa_hash') == torrent_hash]
                    hash_match = len(history_entry) > 0

                if log_entries:
                    Logger.debug(
                        f"Watchlist: {watchlist_entry.get('name', 'Unknown Watchlist')}\n"
                        f" - Tags     (Match={tag_match}): {tags}\n"
                        f" - RegEx    (Match={regex_match}): {regexes}\n"
                        f" - Ex.RegEx (Match={ex_regex_match}): {ex_regexes}\n"
                        f" - Hash     (Match={hash_match}): {torrent_hash}"
                    )
                    if watchlist_entry == watchlist[-1]:
                        Logger.debug()

                # Add to queue if not already downloaded
                if match and not hash_match and not ex_regex_match:
                    torrent['webhooks'] = watchlist_entry.get("webhooks", [])
                    torrent['uploader'] = sub_name
                    torrent['watchlist'] = watchlist_entry.get('name', "Unknown Watchlist")
                    queue.append(torrent)

                    if log_entries:
                        Logger.debug("Torrent added to download list.")
                    break

        if sub_name:
            Config.set_previous_hash(sub_name, feed.entries[0].get('nyaa_infohash', ""))
        return _sort_torrents(queue)

    def fetch_all_feeds(self) -> list:
        """
        Fetches all RSS feeds from the subscriptions and filters the torrents based on the watchlist.
        :return: A list of dictionaries, each representing a torrents from all subscriptions to be downloaded.
        """
        queue = []
        Logger.log()
        for sub in self.subscriptions.get("subscriptions"):
            Logger.log(f"Searching for new uploads from '{sub.get('username')}'...")
            queue += self.fetch_feed(sub.get('rss'), sub.get('watchlist'), sub.get('username'), sub.get('previous_hash'))
        return queue
