[![Nyaa Watcher Banner](https://raw.githubusercontent.com/resort-io/assets/main/nyaa-watcher/img/banner.png)](https://github.com/resort-io/nyaa-watcher)

# Setup

* [Get Started](#get-started)
* [Docker](#docker)
* [Files](#files)
  * [*config.json*](#configjson)
  * [*history.json*](#historyjson)
  * [*watchlist.json*](#watchlistjson)
  * [*webhooks.json*](#webhooksjson)
* [Regular Expressions](#regular-expressions)
* [Example Notifications](#example-notifications)

## Get Started

The watcher will generate JSON files on initial startup or if they are missing from the `/watcher` container directory. Also, the watcher will need to be restarted when making any changes to the files.

**To begin watching** follow these steps:

1. Add an entry to `watchlist.json` with a `name` value and at least one `tag` and/or `regex` value.
2. Add a Nyaa RSS URL to `config.json` within the `nyaa_rss` property.
3. (Optional) Add an entry to `webhooks.json` with `name` and `url` values, and place the `name` within one or more `watchlist.json` entries.
4. Restart the watcher.

### Triggering Download 

The watcher will download a torrent file when **one of three conditions** are true:

* When **one or more** `tag` value matches a string sequence and there are **no** `regex` patterns presents.
* When **one or more** `regex` patterns matches a string sequence and there are **no** `tag` values present.
* When both **one or more** `tag` value and **one or more** `regex` pattern matches a string sequence.

## Docker

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
  -e SHOW_TIPS=false
  -v /path/to/torrent-client/watch:/downloads
  -v /path/to/appdata/nyaa-watcher:/watcher
  --restart unless-stopped
  resortdocker/nyaa-watcher:latest
```

### Parameters

The syntax for the volume parameter is `<host>:<container>`.

| Parameter      | Description                                                                    |
|----------------|--------------------------------------------------------------------------------|
| `-v /watch`    | Watch directory for your torrent client.                                       |
| `-v /watcher`  | Directory for Nyaa Watcher files.                                              |
| `-e LOG_LEVEL` | Log information level (Optional). `INFO` (default) or `DEBUG`                  |
| `-e SHOW_TIPS` | Show tips in the log from the watcher (Optional) . `true` (default) or `false` |


## Files

### `config.json`

Contains the configuration information for the watcher.

* `nyaa_rss [str]` - URL for a Nyaa user's RSS feed.
* `interval_sec [int]` - Number of seconds between each RSS fetch. Must be **equal to or greater than 60 seconds**.
* `version [str]` - Version of the watcher.

```json
{
    "nyaa_rss": "https://nyaa.si/?page=rss&u=NYAA_USERNAME",
    "interval_sec": 600,
    "version": "1.1.2"
}
```

### `history.json`

Contains lists of information for each successful and failed torrent downloads. Used to prevent duplicate downloads.

* `errors [list]` - List of failed downloads.
* `history [list]` - List of successful downloads.

Each entry contains the following properties:

* `torrent_title [str]` - Title of the torrent.
* `date_downloaded | date_failed [datetime]` - Date and time when the torrent file downloaded/failed.
* `nyaa_page [str]` - Nyaa page URL for the torrent.
* `nyaa_hash [str]` - Unique identifier of the torrent.

```json
{
  "errors": [],
  "history": []
}
```

### `watchlist.json`

Contains each of the series you want to the watcher to download.

* `name [str]` - Name for to identify the entry (Not used when searching).
* `tags [list]` - List of strings to search for within torrent titles.
* `regex [list]` - List of regular expression patterns to search for within torrent titles (No delimiters or flags).
* `webhooks [list]` - (**Optional**) List of strings with the `name` values from `webhooks.json` that will be notified when a torrent file downloads.

Each watchlist entry must have `name` value and **at least one `tag` or `regex`** value.

```json
{
  "watchlist": [
    {
      "name": "",
      "tags": [],
      "regex": [],
      "webhooks": []
    }
  ]
}
```

See [Regular Expressions](#regular-expressions) below for more information.

#### Example `watchlist.json`

* `Demon Slayer` - Watcher downloads a torrent file when the title contains "***Demon Slayer***" or "***Kimetsu no Yaiba***" **and** is numbered **using the `S00E00` format**.
* `One Piece` - Watcher downloads a torrent file when the title contains "***One Piece - XXXX***" with an **episode number greater than *1063***.

```json
{
  "watchlist": [
    {
      "name": "Nyaa Username - Demon Slayer",
      "tags": ["Demon Slayer", "Kimetsu no Yaiba"],
      "regex": ["S0[0-9]E[0-9][0-9]"],
      "webhooks": ["Friends Server"]
    },
    {
      "name": "Nyaa Username - One Piece",
      "tags": [],
      "regex": ["One Piece - (1[0-9][6-9][3-9]|[1-9][0-9][7-9][0-9]|[1-9][1-9][0-9]{2}|[2-9][0-9]{3})"],
      "webhooks": ["Notification Server"]
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

**Note**: A single webhook URL can be used for multiple webhooks.

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

#### Torrent Info Tokens

Insert torrent information into the `title` and `description` values in the notification:

* `$webhook_name` - Name of the webhook.
* `$title` - Title of the torrent.
* `$downloads` - Number of downloads for the torrent.
* `$seeders` - Number of seeders for the torrent.
* `$leechers` - Number of leechers for the torrent.
* `$size` - Size of the torrent (e.g., *178.2 MiB*).
* `$published` - Date and time the torrent was published (e.g., *Fri, 20 Apr 2023 20:47*).
* `$category` - Nyaa category for the torrent (e.g., *Anime - English-translated*).

#### Torrent Info Placement

The **`show_` properties** represent where torrent information will be placed within the notification on a **3x2** grid, ranging from `0` to `6`:

* `0` - **Disabled**
* `1` - **Top Left**
* `2` - **Top Middle**
* `3` - **Top Right**
* `4` - **Bottom Left**
* `5` - **Bottom Middle**
* `6` - **Bottom Right**

See the [Example Notifications](#example-notifications) section for images of notifications.

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
        "title": "Nyaa User uploaded a new torrent!",
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

Visit [Regex101](https://regex101.com/) for more information on creating and testing patterns.

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
