import feedparser
import os
import re
from config import Config
from feedparser import FeedParserDict
from logger import Logger


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

    def append_to_history(self, torrents: list[dict]) -> None:
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

        downloads: list[dict] = self.history.get('downloads')

        for torrent in torrents:
            downloads.append({
                "uploader": torrent.get('uploader'),
                "torrent_title": torrent.get('title'),
                "date_downloaded": torrent.get('download_datetime'),
                "nyaa_page": torrent.get('id'),
                "nyaa_hash": torrent.get('nyaa_infohash')
            })

    def fetch_feed(self, rss: str, sub_name: str, prev_hash: str = None, watchlist: list[dict] = None) -> list:
        """
        Fetches an RSS feed and filters the torrents based on the watchlist.
        :param rss: The URL of the RSS feed (E.g., https://nyaa.si/?page=rss&u=Username).
        :param watchlist: The `watchlist` property from a `subscriptions` entry.
        :param sub_name: The `username` property from a `subscriptions` entry.
        :param prev_hash: The most recent torrent hash of the previous fetch. The `previous_hash` property from a `subscriptions` entry.
        :return: A list of dictionaries, containing matched torrents fetched from the `rss` param.
        """

        # log_entries: bool = os.environ.get("LOG_RSS_ENTRIES", "false").lower() == "true"
        feed: FeedParserDict = feedparser.parse(rss)

        if len(feed.entries) == 0:
            Logger.log(f"Unknown Error: No uploads from {rss}.")
            return []

        download_queue = []
        for torrent in feed.entries:
            title: str = torrent.get('title')
            torrent_hash: str = torrent.get('nyaa_infohash')

            # Check if the torrent file has fetched previously
            if torrent_hash == prev_hash:
                Logger.debug(f"Found previously fetched torrent: {title}")
                break

            Logger.debug(f"Reading: {title}")

            # TODO: Create an optional global `webhooks` property for `subscription` entries
            # all_webhooks: list[str] = []

            if watchlist and len(watchlist) > 0:
                for watchlist_entry in watchlist:
                    tag_match = regex_match = ex_regex_match = hash_match = False

                    # Checking tags
                    tags: list[str] = watchlist_entry.get("tags", [])
                    for tag in tags:
                        if tag.lower() in title.lower():
                            tag_match = True
                            break

                    # Checking regex
                    regexes: list[str] = watchlist_entry.get("regex", [])
                    for regex_pattern in regexes:
                        pattern = re.compile(regex_pattern)
                        if re.search(pattern, title):
                            regex_match = True
                            break

                    # Checking excluded regex
                    ex_regexes: list[str] = watchlist_entry.get("exclude_regex", [])
                    for regex_pattern in ex_regexes:
                        pattern = re.compile(regex_pattern)
                        if re.search(pattern, title):
                            ex_regex_match = True
                            break

                    match: bool = (tag_match or not tags) and (regex_match or not regexes)
                    if ex_regex_match:
                        match = False

                    # Checking if torrent has been downloaded
                    if match:
                        history_entry = [(entry['nyaa_hash'], entry) for entry in self.history.get("downloads") if entry.get('nyaa_hash') == torrent_hash]
                        hash_match = len(history_entry) > 0

                    Logger.debug(
                        f"Watchlist: {watchlist_entry.get('name', 'Unknown Watchlist')}\n"
                        f" - Tags     (Match={tag_match}): {tags}\n"
                        f" - RegEx    (Match={regex_match}): {regexes}\n"
                        f" - Ex.RegEx (Match={ex_regex_match}): {ex_regexes}\n"
                        f" - History  (Match={hash_match}): {torrent_hash}"
                    )
                    if watchlist_entry == watchlist[-1]:
                        Logger.debug()

                    # Add to queue if not already downloaded
                    if match and not hash_match and not ex_regex_match:
                        torrent['uploader'] = sub_name
                        torrent['watchlist'] = watchlist_entry.get('name', "Unknown Watchlist")
                        torrent['webhooks'] = watchlist_entry.get("webhooks", [])
                        download_queue.append(torrent)

                        Logger.debug("Torrent added to download queue.")
                        break

            # No `watchlist` property
            else:
                # Checking if torrent has been downloaded
                history_entry = [(entry['nyaa_hash'], entry) for entry in self.history.get("downloads") if entry.get('nyaa_hash') == torrent_hash]
                hash_match = len(history_entry) > 0

                Logger.debug(f" - History (Match={hash_match}): {torrent_hash}")

                if not hash_match:
                    torrent['uploader'] = sub_name
                    torrent['webhooks'] = []
                    download_queue.append(torrent)

                    Logger.debug("Torrent added to download queue.")

        Config.set_previous_hash(sub_name, feed.entries[0].get('nyaa_infohash', ""))
        self.set_previous_hash(sub_name, feed.entries[0].get('nyaa_infohash', ""))
        return _sort_torrents(download_queue)

    def fetch_all_feeds(self) -> list:
        """
        Fetches all RSS feeds from the subscriptions and filters the torrents based on the watchlist.
        :return: A list of dictionaries, containing matched torrents fetched from all subscriptions.
        """

        queue = []
        Logger.log()
        for sub in self.subscriptions.get("subscriptions"):
            Logger.log(f"Searching for new uploads from '{sub.get('username')}'...")
            queue += self.fetch_feed(sub.get('rss'), sub.get('username'), sub.get('previous_hash'), sub.get('watchlist', []))
        return queue

    def set_previous_hash(self, sub_name: str, hash_value: str) -> None:
        for sub in self.subscriptions.get("subscriptions"):
            if sub.get('username') == sub_name:
                sub['previous_hash'] = hash_value or sub['previous_hash']
                break
