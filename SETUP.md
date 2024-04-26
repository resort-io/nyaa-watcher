[![Nyaa Watcher Banner](https://raw.githubusercontent.com/resort-io/assets/main/nyaa-watcher/img/banner.png)](https://github.com/resort-io/nyaa-watcher)

# Setup

* [Getting Started](#getting-started)
* [Docker](#docker)
* [Files](#files)
  * [*config.json*](#configjson)
  * [*history.json*](#historyjson)
  * [*subscriptions.json*](#subscriptionsjson)
  * [*webhooks.json*](#webhooksjson)
* [Regular Expressions](#regular-expressions)
* [Example Notifications](#example-notifications)

## Getting Started

The watcher will generate JSON files on initial startup or if they are missing from the `/watcher` container directory. Also, the watcher will need to be restarted when making any changes to the files.

**To begin watching** follow these steps:

1. Start the watcher to generate the JSON files.
2. Add in `interval_sec` value to `subscriptions.json`.
3. Add an entry to `subscriptions.json` with a `username` value and an `rss` value of the user's RSS URL.
4. Add a `watchlist` entry to the subscription with at least one `tag` and/or `regex` value.
5. (Optional) Add an entry to `webhooks.json` with `name` and `url` values, and place the `name` value in one or more watchlist entries in the `webhooks` property.
6. Restart the watcher.

> Visit the [nyaa-watcher Wiki](https://github.com/resort-io/nyaa-watcher/wiki) for more information on Getting Started.

### Triggering Download

The watcher will download a torrent file when one of the following conditions are met with the title of the torrent:

* **One or more** `tag` value matches a string sequence and there are **no** `regex` patterns present.
* **One or more** `regex` pattern matches a string sequence and there are **no** `tag` values present.
* Both **one or more** `tag` value and **one or more** `regex` pattern matches a string sequence.

In any case, if a `exclude_regex` pattern matches a string sequence, the torrent file will **not** be downloaded.

## Docker

All image tags can be found on [Docker Hub](https://hub.docker.com/r/resortdocker/nyaa-watcher/tags).

```docker
docker run
  --name=nyaa-watcher
  -v /path/to/torrent-client/watch:/downloads
  -v /path/to/appdata/nyaa-watcher:/watcher
  --restart unless-stopped
  resortdocker/nyaa-watcher:latest
```

```docker
docker run
  --name=nyaa-watcher
  -e LOG_LEVEL=DEBUG
  -e LOG_TIPS=false
  -v /path/to/torrent-client/watch:/downloads
  -v /path/to/appdata/nyaa-watcher:/watcher
  --restart unless-stopped
  resortdocker/nyaa-watcher:latest
```

### Parameters

The syntax for the volume parameter is `<host>:<container>`.

| Parameter       | Description                                                   |
|-----------------|---------------------------------------------------------------|
| `-v /downloads` | Directory for downloaded torrent files.                       |
| `-v /watcher`   | Directory for watcher JSON files.                             |
| `-e LOG_LEVEL`  | Log information level (Optional). `INFO` (default) or `DEBUG` |
| `-e LOG_TIPS`   | Show tips in the log (Optional). `true` (default) or `false`  |


## Files

### `config.json`

Contains the configuration for the watcher.

* `version [str]` - Version of the watcher.

```json
{
    "version": "1.2.0"
}
```

### `history.json`

Contains lists of information for each successful and failed torrent downloads. Used to prevent duplicate downloads.

* `downloads [list]` - List of successful downloads.
* `errors [list]` - List of failed downloads.

Each entry contains the following properties:

* `uploader [str]` - Nyaa username of the uploader.
* `torrent_title [str]` - Title of the torrent.
* `date_downloaded | date_failed [datetime]` - Date and time when the torrent file downloaded/failed.
* `nyaa_page [str]` - Nyaa page URL of the torrent.
* `nyaa_hash [str]` - Unique identifier of the torrent.

```json
{
    "downloads": [],
    "errors": []
}
```

### `subscriptions.json`

Contains each user's RSS feed and the uploads you want to watch.

* `interval_sec [int]` - Number of seconds between each RSS fetch. Must be **equal to or greater than 60 seconds**.
* `subscriptions [list]` - List of Nyaa RSS feeds to watch.
  * `username [str]` - Nyaa username for the RSS feed.
  * `rss [str]` - RSS URL for the Nyaa user's feed.
  * `watchlist [list]` - List of watchlist entries.
    * `name [str]` - Name for to identify the entry (Not used when searching) (Optional).
    * `tags [list]` - List of strings to search for within torrent titles.
    * `regex [list]` - List of regular expression patterns to search for within torrent titles (No delimiters or flags).
    * `exclude_regex [list]` - List of regular expression patterns to search for within torrent titles, and will prevent a torrent file from downloading if found (No delimiters or flags) (Optional). 
    * `webhooks [list]` - List of strings with the `name` values from `webhooks.json` that will be notified when a torrent file downloads (Optional).
  * `previous_hash [str]` - Previous hash value of the RSS feed (Automatically updated by the watcher).

Each `subscriptions` entry must have a `username`, `rss`, and a `watchlist` value.

Each `watchlist` entry must have and **at least one `tag` or `regex`** value. All other values are optional.

> Generate a custom `subscriptions.json` JSON string with [this online Python script](https://www.online-python.com/5w9JMmfQid).

```json
{
    "interval_sec": 600,
    "subscriptions": [
        {
            "username": "Username",
            "rss": "https://nyaa.si/?page=rss&u=USERNAME",
            "watchlist": [
                {
                    "name": "",
                    "tags": [],
                    "regex": [],
                    "exclude_regex": [],
                    "webhooks": []
                }
            ],
            "previous_hash": ""
        }
    ]
}
```

> See [Regular Expressions](#regular-expressions) below for more information.

#### Example `subscriptions.json`

Each `watchlist` entry must contain at least one `tag` and/or `regex` value. The `name`, `exclude_regex`, and `webhooks` values are optional.

```json
{
    "interval_sec": 600,
    "subscriptions": [
        {
            "username": "Foo",
            "rss": "https://nyaa.si/?page=rss&u=Foo",
            "watchlist": [
                {
                    "name": "Demon Slayer",
                    "tags": [
                        "Demon Slayer",
                        "Kimetsu no Yaiba"
                    ],
                    "regex": [
                        "S[0-9]{2}E[0-9]{2}"
                    ],
                    "webhooks": [
                        "Friends Server"
                    ]
                },
                {
                    "name": "Unnamed Memory",
                    "regex": [
                        "One Piece - (1[0-9][6-9][3-9]|1[0-9][7-9][0-9]|1[1-9][0-9]{2}|[2-9][0-9]{3})"
                    ],
                    "exclude_regex": [
                        "x264"
                    ],
                    "webhooks": [
                        "Notification Server"
                    ]
                }
            ],
            "previous_hash": "23870945yufh2w837u49ifwh0834957ufh203847"
        },
        {
            "username": "Bar",
            "rss": "https://nyaa.si/?page=rss&u=Bar",
            "watchlist": [
                {
                    "tags": [
                        "My Hero Academia",
                        "Boku no Hero Academia"
                    ]
                }
            ],
            "previous_hash": "09q873w4yt0qw9834yhfg089yq083794uyf7689r"
          }
    ]
}
```

### `webhooks.json`

Contains the information for the Discord webhooks and notification customization.

* `name [str]` - Name to the webhook. This is the value used in the `webhooks` property in `watchlist.json`.
* `url [str]` - URL for the Discord webhook.
* `notifications [dict]` - Customization for the notification.
  * `title [str]` - Custom title of the Discord notification. **Leave blank for default message**.
  * `description [str]` - Custom description of the Discord notification. **Leave blank for no message**.
  * `show_category [int]` - (0 to 6) Nyaa category for the torrent.
  * `show_downloads [int]` - (0 to 6) Number of downloads for the torrent.
  * `show_leechers [int]` - (0 to 6) Number of leechers for the torrent.
  * `show_published [int]` - (0 to 6) Date and time the torrent was published. 
  * `show_seeders [int]` - (0 to 6) Number of seeders for the torrent.
  * `show_size [int]` - (0 to 6) Size of the torrent.

Multiple `webhooks.json` entries can use the same `url` value.

> Generate a custom `webhooks.json` JSON string with [this online Python script](https://www.online-python.com/tmoXYrqd6A).

```json
{
    "webhooks": [
        {
            "name": "",
            "url": "",
            "notifications": {
                "title": "",
                "description": "",
                "show_category": 0,
                "show_downloads": 0,
                "show_leechers": 0,
                "show_published": 0,
                "show_seeders": 0,
                "show_size": 0
            }
        }
    ]
}
```

### Torrent Info Tokens

Use tokens to insert torrent information into the `title` and `description` values:

* `$category` - Nyaa category for the torrent (e.g., *Anime - English-translated*).
* `$downloads` - Number of downloads for the torrent.
* `$leechers` - Number of leechers for the torrent.
* `$published` - Date and time the torrent was published (e.g., *Fri, 20 Apr 2023 20:47*).
* `$seeders` - Number of seeders for the torrent.
* `$size` - Size of the torrent (e.g., *178.2 MiB*).
* `$title` - Title of the torrent.
* `$uploader` - Nyaa username of the uploader.
* `$watchlist` - Name of the watchlist entry (Defaults to *Unknown Watchlist*).
* `$webhook` - Name of the webhook.

### Torrent Info Placement

The **`show_` properties** represent where torrent information will be placed within the notification on a **3x2** grid, ranging from `0` to `6`:

* `0` - **Disabled**
* `1` - **Top Left**
* `2` - **Top Middle**
* `3` - **Top Right**
* `4` - **Bottom Left**
* `5` - **Bottom Middle**
* `6` - **Bottom Right**

> See the [Example Notifications](#example-notifications) section for images of notifications.

#### Example `webhooks.json`

* `Friends Server` - Sends a notification with a **custom title** and ** custom description**, plus the **size** and **published date** properties.
* `Notifications Server` - Sends a notification with the **default title** and **all six** properties in a custom order.

```json
{
    "webhooks": [
        {
            "name": "Friends Server",
            "url": "https://discord.com/api/webhooks/RANDOM_STRING/RANDOM_STRING",
            "notifications": {
                "title": "$uploader uploaded a new torrent!",
                "description": "Starting download for $title.",
                "show_category": 0,
                "show_downloads": 0,
                "show_leechers": 0,
                "show_published": 2,
                "show_seeders": 0,
                "show_size": 1
            }
        },
        {
            "name": "Notifications Server",
            "url": "https://discord.com/api/webhooks/RANDOM_STRING/RANDOM_STRING",
            "notifications": {
                "title": "",
                "description": "",
                "show_category": 3,
                "show_downloads": 4,
                "show_leechers": 6,
                "show_published": 1,
                "show_seeders": 5,
                "show_size": 2
            }
        }
    ]
}
```

## Regular Expressions

Below are examples of regular expressions that can be modified for your needs.

Titles with the `00` format may the words ***720p*** or ***1080p*** within them which will interfere with the matching,
so you may want to use a `regex` value with both the title and episode number pattern.

> Visit [Regex101](https://regex101.com/) for more information on creating and testing patterns.

### Regular Expression Examples

#### `S00E00` Format

| Expression                                           | Use Case                                                      |
|------------------------------------------------------|---------------------------------------------------------------|
| `E(0[5-9]\|[1-9][0-9])`                              | Matches an **episode number >=5**.                            |
| `E([1-9][2-9]\|[2-9][0-9])`                          | Matches an **episode number >=12**.                           |
| `S(09\|[1-9][0-9])`                                  | Matches a **season number >=9**.                              |
| `S[1-9][0-9]`                                        | Matches a **season number >=10**.                             |
| `S([1-9][1-9]\|[2-9][0-9])E([1-9][3-9]\|[2-9][0-9])` | Matches a **season number >=11** and **episode number >=13**. |

#### `00` Format

| Expression                                                          | Use Case                              |
|---------------------------------------------------------------------|---------------------------------------|
| `[1-9][0-9]{0,3}`                                                   | Matches an **episode number >=1**.    |
| `[1-9][0-9]{1,3}`                                                   | Matches an **episode number >=10**.   |
| `[1-9][0-9]{2,3}`                                                   | Matches an **episode number >=100**.  |
| `[1-9][0-9]{3}`                                                     | Matches an **episode number >=1000**. |
| `7[4-9][9-9]\|[7-9][5-9][0-9][8-9][0-9]{2}\|[1-9][0-9]{3}`          | Matches an **episode number >=749**.  |
| `1[4-9][5-9][3-9]\|1[4-9][6-9][0-9]\|1[5-9][0-9]{2}\|[2-9][0-9]{3}` | Matches an **episode number >=1453**. |

### Example Notifications

`Friends Server`

![Nyaa Watcher Webhook Notification Example #1](https://raw.githubusercontent.com/resort-io/assets/main/nyaa-watcher/img/notification-example-1.png)

`Notifications Server`

![Nyaa Watcher Webhook Notification Example #2](https://raw.githubusercontent.com/resort-io/assets/main/nyaa-watcher/img/notification-example-2.png)

## More Information

Visit the [nyaa-watcher Wiki](https://github.com/resort-io/nyaa-watcher/wiki) for more information.