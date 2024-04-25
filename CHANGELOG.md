[![Nyaa Watcher Banner](https://raw.githubusercontent.com/resort-io/assets/main/nyaa-watcher/img/banner.png)](https://github.com/resort-io/nyaa-watcher)

# Changelog

## [1.2.0](https://github.com/resort-io/nyaa-watcher/releases/tag/v1.2.0) *(04/26/2024)*

* Added feature to watch and download torrents from multiple Nyaa RSS feeds.
  * Renamed `watchlist.json` to `subscriptions.json`.
  * Added `subscriptions` property to `subscriptions.json`.
  * Added `previous_hash` property to `subscriptions.json` entries.
  * Added `uploader` property to `history.json` entries.
  * Added `$uploader` and `$watchlist` string tokens. 
  * Moved the `nyaa_rss` and `interval_sec` properties from `config.json` into `subscriptions.json`.
* Added `excl_regex` property to watchlist entries in `subscriptions.json`.
* Changed `subscriptions.json` verification to only require at least one `tag` or `regex` value; all other values are optional.
* Removed initial RSS connection test.
* Renamed `$webhook_name` string token to `$webhook`.
* Renamed `SHOW_TIPS` environment variable to `LOG_TIPS`.

## [1.1.2](https://github.com/resort-io/nyaa-watcher/releases/tag/v1.1.2) *(04/16/2024)*

* Added `error` property in *history.json* to store failed download information.
* Added `version` property in *config.json*.
* Renamed `history` property to `downloads` in *watchlist.json* .
* Renamed `watcher_interval_seconds` to `interval_sec` in *config.json*.
* Renamed `/watch` container directory to `/downloads`.
* Updated `downloaded_date` result to be more accurate for *history.json*.
* Updated JSON file verification and changed it to only execute at startup (instead of executing before every write).
* Updated RSS fetch function to only read the latest entries since the previous fetch.
* Updated logging to show successful and failed downloads.

## [1.1.1](https://github.com/resort-io/nyaa-watcher/releases/tag/v1.1.1) *(07/17/2023)*

* Added function that inserts the missing `webhooks` property in *watchlist.json* entries.
* Added function that adds a sample entry in *webhooks.json* when the file is empty.
* Changed `watcher_interval_seconds` to be a minimum of **60** seconds.
* Updated *searching for torrents* log message to be a complete sentence.

## [1.1.0](https://github.com/resort-io/nyaa-watcher/releases/tag/v1.1.0) *(07/01/2023)*

* Added Discord webhook support; server sends custom notification via Discord webhook(s) when a torrent file downloads.
  * Created *webhooks.json* and added optional `webhooks` property to *watchlist.json* entries.
* Changed *searching for torrents* log message from seconds into minutes.
* Updated startup and error log messages to include more specific information.

## [1.0.1](https://github.com/resort-io/nyaa-watcher/releases/tag/v1.0.1) *(06/04/2023)*

* Added log messages during startup when testing RSS URL.
* Fixed *watchlist.json* file validation check.

## [1.0.0](https://github.com/resort-io/nyaa-watcher/releases/tag/v1.0.0) *(06/01/2023)*

* Initial release.