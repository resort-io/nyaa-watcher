# Changelog

## [1.1.2](https://github.com/resort-io/nyaa-watcher/releases/tag/v1.1.2) *(04/16/2024)*

* Added `error` property in *history.json* to store failed download information.
* Added `version` property in *config.json*.
* Renamed `history` property to `downloads` in *watchlist.json* .
* Renamed `watcher_interval_seconds` to `interval_sec` in *config.json*.
* Renamed `/watch` container directory to `/downloads`.
* Updated `downloaded_date` results for *history.json* to be more accurate.
* Updated RSS fetch function to only read the latest entries since the previous fetch.
* Updated logging to show successful and failed downloads.
* Removed JSON file verifications from every write (Files now are only verified at startup).

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