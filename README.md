[![Nyaa Watcher Banner](https://raw.githubusercontent.com/resort-io/assets/main/nyaa-watcher/img/banner.png)](https://github.com/resort-io/nyaa-watcher)

[![resort-io GitHub Repositories](https://img.shields.io/static/v1.svg?color=0085ff&labelColor=555555&logoColor=ffffff&style=for-the-badge&label=resort-io&message=all-repositories&logo=github)](https://github.com/resort-io "All GitHub repositories from resort-io")
[![resortdocker Docker Repositories](https://img.shields.io/static/v1.svg?color=0085ff&labelColor=555555&logoColor=ffffff&style=for-the-badge&label=resortdocker&message=all-repositories&logo=docker)](https://hub.docker.com/u/resortdocker "All Docker repositories from resortdocker")

[![Nyaa Watcher GitHub Repository](https://img.shields.io/static/v1.svg?color=0085ff&labelColor=555555&logoColor=ffffff&style=for-the-badge&label=github&message=nyaa-watcher&logo=github)](https://github.com/resort-io/nyaa-watcher "Source code of Nyaa Watcher")
[![Latest GitHub Release](https://img.shields.io/github/v/release/resort-io/nyaa-watcher?color=0085ff&logo=github&style=for-the-badge)](https://github.com/resort-io/nyaa-watcher/releases "Latest GitHub release")
[![Latest Docker Image Tags](https://img.shields.io/docker/v/resortdocker/nyaa-watcher?color=0085ff&logo=docker&logoColor=white&style=for-the-badge)](https://hub.docker.com/r/resortdocker/nyaa-watcher/tags "Latest Docker Image Tags")
![Docker Pulls](https://img.shields.io/docker/pulls/resortdocker/nyaa-watcher?color=0085ff&label=pulls&logo=docker&logoColor=white&style=for-the-badge)

## Table of Contents

   * [Features](#features)
     * [Upcoming Updates](#upcoming-updates)
   * [Usage](#usage)
      * [docker cli](#docker-cli)
      * [docker compose](#docker-compose)
      * [Parameters](#parameters)
   * [Startup](#startup)
   * [Configuration](#configuration)
      * [Files](#files)
         * [*config.json*](#configjson)
         * [*history.json*](#historyjson)
         * [*watchlist.json*](#watchlistjson)
            * [Example *watchlist.json*](#example-watchlistjson)
         * [*webhooks.json*](#webhooksjson)
            * [Example *webhooks.json*](#example-webhooksjson)
            * [Example Notification Images](#example-notification-images)
      * [Regular Expression Samples](#regular-expression-samples)
      * [Regular Expression Samples Guide](#regular-expression-samples-guide)
   * [Issues](#issues)
   * [Feature Request](#feature-requests)
   * [Versions](#versions)

## Features

* Monitors any Nyaa RSS feed for titles, and downloads the torrent files into a torrent client watch directory.
* Uses custom tags and/or regular expressions to search and filter for specific titles.
* Notifies Discord channels via webhooks when a torrent file downloads.
* Maintains a history backlog to store torrent information and prevent duplicate downloads.

### Upcoming Updates

* Multiple Nyaa RSS feeds.
* Unraid community app support.

## Usage

Examples for creating the container:

### [docker cli](https://docs.docker.com/engine/reference/commandline/cli/)

```bash
docker run
  --name=nyaa-watcher
  -e PUID=1000 #optional
  -e PGID=1000 #optional
  -e LOG_LEVEL="INFO" #optional
  -v /path/to/torrent-client/watch:/watch
  -v /path/to/appdata/nyaa-watcher:/watcher
  --restart unless-stopped
  resortdocker/nyaa-watcher:latest
```

### [docker compose](https://docs.docker.com/compose/compose-file/)

```bash
---
version: "3.8"
services:
  nyaa-watcher:
    image: resortdocker/nyaa-watcher:latest
    container_name: nyaa-watcher
    environment:
      - PUID=1000 #optional
      - PGID=1000 #optional
      - LOG_LEVEL="INFO" #optional
    volumes:
      - /path/to/torrent-client/watch:/watch
      - /path/to/appdata/nyaa-watcher:/watcher
    restart: unless-stopped
```

### Parameters

Volume parameter syntax is `<host>:<container>`.

| Parameter      | Function                                                                     |
|----------------|------------------------------------------------------------------------------|
| `-v /watch`    | Watch directory for your torrent client.                                     |
| `-v /watcher`  | Directory for Nyaa Watcher files.                                            |
| `-e PUID=1000` | Optional (Depending on your host machine) - UserID for volume permissions.   |
| `-e PGID=1000` | Optional (Depending on your host machine) - GroupID  for volume permissions. |
| `-e LOG_LEVEL` | Optional - Log information level. `INFO` or `DEBUG`                          |

## Startup

The server will generate the following files on startup: `config.json`, `history.json`, `watchlist.json`, and `webhooks.json`.
These files will regenerate if any are removed or deleted.

**To begin watching**, follow the instructions given by the log messages:

* Add an entry including a title with tag(s), and optional regex(es) values to filter the results in `watchlist.json`.
* Add a Nyaa RSS URL to `config.json`.
* Add optional Discord webhook(s) entry to `webhooks.json` and place the name(s) inside the `webhooks` array in `watchlist.json` entries.

The server will need to be restarted when making changes to any file.

See [Files](#files) below for more information on getting started.

## Configuration

### Files

#### `config.json`

Contains the information necessary for the server.

* `nyaa_rss` - URL for a Nyaa user's RSS feed.
* `watcher_interval_seconds` - Interval between each RSS torrent fetch.

```json
{
  "nyaa_rss": "https://nyaa.si/?page=rss&u=NYAA_USERNAME",
  "watcher_interval_seconds": 600
}
```

#### `history.json`
Contains a list of information for each downloaded torrent.
Used to prevent duplicate downloads, **do not modify**.

* `torrent_title` - Title of the torrent.
* `date_downloaded` - Date and time the torrent file was downloaded.
* `nyaa_page` - Nyaa page URL for the torrent.
* `nyaa_hash` - Unique identifying hash of the torrent.


#### `watchlist.json`
Contains the tags and regular expressions that the server will search for in the torrent titles,
as well as the names of the Discord webhook entries.

**To create a watchlist entry**, enter a value in the `name` field, and one or more values in the `tags` and/or `regex` fields.

The server will download a torrent file when **one of three scenarios** are true:
1. When **one or more** `tag` values match a string sequence within the torrent title, and there are **no** `regex` values in the watchlist entry.
2. When **one or more** `regex` patterns match a string sequence within the torrent title, and there are **no** `tag` values in the watchlist entry.
3. When **both** a `tag` and `regex` value match a string sequence within the torrent title.

**Each watchlist entry must have at least one `tag` or `regex` value**.

* `name` - Name for you to identify the entry. Not used when searching.
* `tags` - Array of strings to search for in each torrent title.
* `regex` - Array of regular expression patterns to filter results found from `tags`, or can be used independently (No delimiters or flags).
* `webhooks` - **Optional**: Array of strings holding the `name` values of the Discord webhooks from `webhooks.json` that will
               be notified when a torrent file downloads.

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

#### Example `watchlist.json`

* `Demon Slayer` - Download triggers when a torrent title contains "***Demon Slayer***" or "***Kimetsu no Yaiba***",
   and is a weekly release **using the `S00E00` format**.
* `One Piece` - Download triggers when a torrent title contains "***One Piece - XXXX***" with an **episode number greater than *1063***.

```json
{
  "watchlist": [
    {
      "name": "Nyaa Username - Demon Slayer",
      "tags": ["Demon Slayer", "Kimetsu no Yaiba"],
      "regex": ["S0[0-9]E[0-9][0-9]"]
    },
    {
      "name": "Nyaa Username - One Piece",
      "tags": [],
      "regex": ["One Piece - ([1-9][0-9][6-9][3-9]|[1-9][0-9][7-9][0-9]|[1-9][1-9][0-9][0-9]|[2-9][0-9][0-9][0-9])"]
    }
  ]
}
```

See [Regular Expressions](#regular-expression-samples) below for more information.

#### `webhooks.json`
Contains the information for Discord webhooks.

A single webhook URL can be used for multiple webhooks.

The **`show_` properties** represent the placement of each of the property Discord notification message.
The properties are placed in a within the **3x2** grid that displays the information from **left to right**.
The properties range from `0` to `6`:
* **`0` == Disabled**
* **`1` == Top Left**
* **`6` == Bottom Right**

See the [Example Notification Images](#example-notification-images) for samples of Discord notifications.

**Optional**: Use placeholders in the `title` and `description` to customize the Discord notification message:

`$webhook_name`, `$title`, `$downloads`, `$seeders`, `$leechers`, `$size`, `$published`, and `$category`.

* `name` - Name to identify webhook. Values used in `watchlist.json`.
* `url` - URL for the Discord webhook.
* `notifications` - Torrent information included with the discord notification.
  * `title` - Custom title of the Discord notification. **Leave blank for default message**.
  * `description` - Custom description of the Discord notification. **Leave blank for no message**.
  * `show_category` - Nyaa category for the torrent. (E.g., *Anime - English-translated*, *Literature - Non-English-translated*)
  * `show_downloads` - Number of downloads for the torrent.
  * `show_leechers` - Number of leechers for the torrent.
  * `show_published` - Date and time the torrent was published. (E.g., *Fri, 21 Apr 2023 20:47*, *Mon, 21 Nov 2022 17:09*)
  * `show_seeders` - Number of seeders for the torrent.
  * `show_size` - Size of the torrent. (E.g., *178.2 MiB*, *32.1 GiB*)

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

#### Example `webhooks.json`

* `Friends Server` - Sends a notification with a **custom title and description**, along with the **size** and **published date** properties.
* `Notifications Server` - Sends a notification with the **default title**, along with **all six** properties in a custom order.

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

#### Example Notification Images

* `Friends Server`

![Nyaa Watcher Webhook Notification Example #1](https://raw.githubusercontent.com/resort-io/assets/main/nyaa-watcher/img/notification-example-1.png)

* `Notifications Server`

![Nyaa Watcher Webhook Notification Example #2](https://raw.githubusercontent.com/resort-io/assets/main/nyaa-watcher/img/notification-example-2.png)

### Regular Expression Samples
Below are some sample regular expressions that search for episodes numbers within the torrent title
using the `S00E00`, `000`, or `0000` formats.
If you have simpler regular expressions to use, then feel free to use those instead.

* Each set of **square brackets** `[]` represents a single digit, with the number(s) inside being the range.
  Range is hyphenated between two numbers (inclusive) or can be single a digit.
* Each set of **parentheses** `()` represents a portion of the expression that can be selected using a **pipe**.
* Each **pipe** `|` represents an **OR** statement. Can be placed inside or outside of parentheses.

**Notes**: You may want to add additional information to the regex for episodes that are numbered numerically, 
as a "***720p***" or "***1080p***" within the torrent title may interfere with the matching.
Also, if a watchlist entry is using `regex` value(s) to search for **episode numbers >0** in the `E00` **format**,
then you will have to change/remove those value(s) once the season is over.

Visit [Regex101](https://regex101.com/) for more information on creating and testing regular expressions.

#### `S00E00` Format

| Expression                                           | Use Case                                                                       |
|------------------------------------------------------|--------------------------------------------------------------------------------|
| `E([0-9][5-9]\|[1-9][0-9])`                          | Matches any torrent with an **episode number >=5**.                            |
| `E([1-9][2-9]\|[2-9][0-9])`                          | Matches any torrent with an **episode number >=12**.                           |
| `S([0-9][9]\|[1-9][0-9])`                            | Matches any torrent with a **season number >=9**.                              |
| `S[1-9][0-9]`                                        | Matches any torrent with a **season number >=10**.                             |
| `S([1-9][1-9]\|[2-9][0-9])E([1-9][3-9]\|[2-9][0-9])` | Matches any torrent with a **season number >=11** and **episode number >=13**. |

#### `0000` Format

Sample expressions do not include episode numbers above 9999.

| Expression                                                                               | Use Case                                                              |
|------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| `[1-9][0-9][0-9]([0-9]\|)`                                                               | Matches any torrent with an **episode number >=100**. Includes >1000. |
| `[1-9][0-9][0-9][0-9]\|[1-9][0-9][1-9]\|[1-9][1-9][0-9]\|[2-9][0-9][0-9]`                | Matches any torrent with an **episode number >=101**. Includes >1000. |
| `[1-9][0-9][0-9][0-9]\|[7-9][4-9][9]\|[7-9][5-9][0-9]\|[8-9][0-9][0-9]`                  | Matches any torrent with an **episode number >=749**.                 |
| `[1-9][0-9][0-9][0-9]`                                                                   | Matches any torrent with an **episode number >=1000**.                |
| `[1-9]([0-9][0-9][1-9]\|[0-9][1-9][0-9]\|[1-9][0-9][0-9])`                               | Matches any torrent with an **episode number >1000**.                 |
| `[1-9][4-9][5-9][3-9]\|[1-9][4-9][6-9][0-9]\|[1-9][5-9][0-9][0-9]\|[2-9][0-9][0-9][0-9]` | Matches any torrent with an **episode number >=1453**.                |

### Regular Expression Samples Guide

#### `S00E00` Format

The **season number >=11** and **episode number >=13** sample expression above is structured as such:

* Season Group 1: `S[1-9][1-9]` **>=S11** - Represents the desired season number you are starting from.
* Season Group 2: `S[2-9][0-9]` **>=S20** - Represents the remaining numbers in the **Tens** and **Ones** positions.
* Episode Group 1: `E[1-9][3-9]` **>=E13** - Represents the desired episode number you are starting from.
* Episode Group 2: `E[2-9][0-9]` **>=E20** - Represents the remaining numbers in the **Tens** and **Ones** positions.

#### `000` and `0000` Formats

The **episode number >=1453** sample expression above is structured as such:

* Group 1: `[1-9][4-9][5-9][3-9]` **>=1459** - Represents the desired episode number you are starting from.
* Group 2: `[1-9][4-9][6-9][0-9]` **>=1460** - Represents the remaining numbers in the **Tens** and **Ones** positions.
* Group 3: `[1-9][5-9][0-9][0-9]` **>=1500** - Represents the remaining numbers in the **Hundreds** position.
* Group 4: `[2-9][0-9][0-9][0-9]` **>=2000** - Represents the remaining numbers in the **Thousands** position.

## Issues

If you encounter any bugs or issues with the server, please create a new [Bug Report](https://github.com/resort-io/nyaa-watcher/issues/new/choose).

## Feature Requests

You can suggest a new feature by creating a new [Feature Request](https://github.com/resort-io/nyaa-watcher/issues/new/choose).

## Versions

### 1.1.0 *(07/01/2023)*
* Added Discord webhook support; server sends custom notification via Discord webhook(s) when a torrent file downloads.
* Created `webhooks.json` and added optional `webhooks` array property to `watchlist.json` entries.
* Changed interval for 'searching for torrents' log message from seconds to minutes.
* Added and changed startup log messages.
* Added and changed error log messages to include more specific information and solutions.

### 1.0.1 *(06/04/2023)*
* Fixed *watchlist.json* file validation check.
* Added log messages during startup when testing RSS URL.

### 1.0.0 *(06/01/2023)*
* Initial release.