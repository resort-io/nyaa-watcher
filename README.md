# Nyaa Watcher

A python server that monitors a Nyaa RSS feed for specific titles and downloads torrent files into a torrent client watch directory.

## Table of Contents

   * [Features](#features)
     * [Future Features](#future-features)
   * [Usage](#usage)
      * [docker cli](#docker-cli)
      * [docker compose](#docker-compose)
      * [Parameters](#parameters)
   * [Configuration](#configuration)
      * [Files](#files)
         * [config.json](#configjson)
         * [history.json](#historyjson)
         * [watchlist.json](#watchlistjson)
      * [Regular Expressions](#regular-expressions)
      * [Regular Expressions Guide](#regular-expressions-guide)
      * [Example Watchlist](#example-watchlist)
   * [Versions](#versions)

## Features

* 

### Future Features

* 

## Usage

### [docker cli](https://docs.docker.com/engine/reference/commandline/cli/)

```bash
docker run
  --name=nyaa-watcher
  -e PUID=1000
  -e PGID=1000
  -e LOG_LEVEL="INFO" #optional
  -v /path/to/torrent-client/watch:/watch
  -v /path/to/appdata/nyaa-watcher:/watcher
  --restart unless-stopped
  USER_NAME/nyaa-watcher:latest
```

### [docker compose](https://docs.docker.com/compose/compose-file/)

```bash
---
version: "2.1"
services:
  nyaa-watcher:
    image: USER_NAME/nyaa-watcher:latest
    container_name: nyaa-watcher
    environment:
      - PUID=1000
      - PGID=1000
      - LOG_LEVEL="INFO" #optional
    volumes:
      - /path/to/torrent-client/watch:/watch
      - /path/to/appdata/nyaa-watcher:/watcher
    restart: unless-stopped
```

### Parameters

Parameter syntax is `<host>:<container>`.

| Parameter      | Function                                            |
|----------------|-----------------------------------------------------|
| `-e PUID=1000` | UserID for volume permissions.                      |
| `-e PGID=1000` | GroupID  for volume permissions.                    |
| `-e LOG_LEVEL` | Optional - Log information level. `INFO` or `DEBUG` |
| `-v /watch`    | Watch directory for torrent client.                 |
| `-v /watcher`  | Directory for Nyaa Watcher files.                   |

## Configuration

The server will generate three files on startup: `config.json`, `history.json`, and `watchlist.json`.
The server will regenerate these files if any are removed or deleted.

The server will need to be restarted when making changes to `config.json` or `watchlist.json`.

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
Contains the list of information for each downloaded torrent.
Used to prevent duplicate downloads, **do not modify**.

* `torrent_title` - Title of the torrent.
* `date_downloaded` - Date and time the torrent file was downloaded.
* `nyaa_page` - Nyaa page URL for the torrent.
* `nyaa_hash` - Unique identifying hash of the torrent.


#### `watchlist.json`
Contains the tags and regular expressions that the server will search for in the RSS feed torrent titles.
Each entry must have at least one tag or one regex value.

* `name` - Name for you to identify the entry. Not used when searching.
* `tags` - Array to strings to search for in each torrent title. Only one tag needs to match.
* `regex` - Array of regular expressions to search for in each torrent title. Only one expression needs to match.

```json
{
  "watchlist": [
    {
      "name": "",
      "tags": [],
      "regex": []
    }
  ]
}
```

See [Regular Expressions](#regular-expressions) and [Example Watchlist](#example-watchlist) below for more information.

### Regular Expressions
Below are some sample regular expressions that search for episodes numbers within the torrent title
using the `S00E00`, `000`, or `0000` formats.

* Each **square bracket** `[0-9]` represents a single digit ranging from the left digit, `0`, to the right digit, `9` (Inclusive).
* Each set of **parentheses** `()` represents a portion of the expression that can be used with a **pipe**.
* Each **pipe** `|` represents an **OR** statement. Placed inside or outside of parentheses.

**Notes**: You may want to add additional information to the regex for episodes that are numbered numerically, 
as a "***720p***" or "***1080p***" within the torrent title may interfere with the matching.
Also, if you are using searching for episode numbers >0 in the `E00` format, then you will have to change/remove
the regex once the season is over.

Visit [Regex101](https://regex101.com/) for more information on creating and testing regular expressions.

#### `S00E00` Format

| Expression                                           | Use Case                                                                     |
|------------------------------------------------------|------------------------------------------------------------------------------|
| `E([0-9][5-9]\|[1-9][0-9])`                          | Matches any torrent with an **episode number >4**.                           |
| `E([1-9][2-9]\|[2-9][0-9])`                          | Matches any torrent with an **episode number >=12**.                         |
| `S([0-9][9]\|[1-9][0-9])`                            | Matches any torrent with a **season number >9**.                             |
| `S[1-9][0-9]`                                        | Matches any torrent with a **season number >=10**.                           |
| `S([1-9][1-9]\|[2-9][0-9])E([1-9][3-9]\|[2-9][0-9])` | Matches any torrent with a **season number >10** and **episode number >12**. |

#### `0000` Format

Sample expressions do not include episode numbers above 9999.

| Expression                                                                               | Use Case                                               |
|------------------------------------------------------------------------------------------|--------------------------------------------------------|
| `[1-9][0-9][0-9]([0-9]\|)`                                                               | Matches any torrent with an **episode number >=100**.  |
| `[1-9][0-9][0-9][0-9]\|[1-9][0-9][1-9]\|[1-9][1-9][0-9]\|[2-9][0-9][0-9]`                | Matches any torrent with an **episode number >100**.   |
| `[1-9][0-9][0-9][0-9]\|[7-9][4-9][9]\|[7-9][5-9][0-9]\|[8-9][0-9][0-9]`                  | Matches any torrent with an **episode number >=749**.  |
| `[1-9][0-9][0-9][0-9]`                                                                   | Matches any torrent with an **episode number >=1000**. |
| `[1-9]([0-9][0-9][1-9]\|[0-9][1-9][0-9]\|[1-9][0-9][0-9])`                               | Matches any torrent with an **episode number >1000**.  |
| `[1-9][4-9][5-9][3-9]\|[1-9][4-9][6-9][0-9]\|[1-9][5-9][0-9][0-9]\|[2-9][0-9][0-9][0-9]` | Matches any torrent with an **episode number >=1453**. |

### Regular Expressions Guide

To modify the expressions for your needs...

### Example Watchlist

The example watchlist has two entries:

* `Demon Slayer` - Download triggers when a torrent title contains "***Demon Slayer***" or "***Kimetsu no Yaiba***".
* `One Piece` - Download triggers when a torrent title contains "***One Piece***" and an episode number greater than ***1063***.

```json
{
  "watchlist": [
    {
      "name": "Nyaa Username - Demon Slayer",
      "tags": ["Demon Slayer", "Kimetsu no Yaiba"],
      "regex": []
    },
    {
      "name": "Nyaa Username - One Piece",
      "tags": [],
      "regex": ["One Piece - [1-9][0-9][6-9][3-9]|[1-9][0-9][7-9][0-9]|[1-9][1-9][0-9][0-9]|[2-9][0-9][0-9][0-9]"]
    }
  ]
}
```

## Versions

* **1.0.0** (06/30/2023): Initial release.