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

**To begin watching** follow these steps:

1. Create a **`subscriptions.json` file** in the `/watcher` container directory.
2. Use the [***subscriptions.json* generator**](https://www.online-python.com/5w9JMmfQid) script to get a **custom JSON string** and **paste it into** `subscriptions.json`.
3. ***(Optional)*** Create a **`webhooks.json` file** in the `/watcher` container directory.
4. ***(Optional)*** Use the [***webhooks.json* generator**](https://www.online-python.com/tmoXYrqd6A) script to get a **custom JSON string** and **paste it into** `webhooks.json`.
5. Start the watcher.

> #### Important Notes
> 
> * Any JSON file that is missing from the `/watcher` container directory will be generated at startup.
> * The watcher will need to be restarted **after making any changes** to a JSON file.

### Triggering Download

The watcher will download a torrent file if **one of the following** conditions are met for a **watchlist entry**:

* When a `tag` value finds a match in the **torrent title** and there are **no** `regex` patterns.
* When a `regex` pattern finds a match in the **torrent title** and there are **no** `tag` values.
* When **both** a `tag` value and a `regex` pattern finds a match in the **torrent title**.

**In any case**, if a **`exclude_regex` pattern** finds a match, the torrent file **will not be downloaded**.

> Visit the [nyaa-watcher Wiki](https://github.com/resort-io/nyaa-watcher/wiki) for more information on Getting Started.

## Docker

Information on pulling the image and creating a container can be found on the [nyaa-watcher Wiki](https://github.com/resort-io/nyaa-watcher/wiki/Docker).

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

Each entry contains:

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

Contains each Nyaa user and the uploads you want to watch.

> #### Important Notes
> 
> * Each `subscriptions` entry must have a `username`, `rss`, and a `watchlist` value. 
> * Each `watchlist` entry must have and **at least one `tag` or `regex`** value. All other values are optional.

* `interval_sec [int]` - **Number of seconds** between each subscriptions search (Must be **at least 60 seconds**).
* `subscriptions [list]` - List of Nyaa subscriptions.
  * `username [str]` - **Name to identify** a subscription.
  * `rss [str]` - **RSS URL** of a Nyaa user.
  * `watchlist [list]` - List of series for the watcher to search for in a subscription.
    * `name [str]` - **Name to identify** a watchlist entry (Optional; not used for searching).
    * `tags [list]` - **List of strings** to search for within **torrent titles**.
    * `regex [list]` - **List of regular expression patterns** to search for within **torrent titles** (No delimiters or flags).
    * `exclude_regex [list]` - **List of regular expression patterns** to search for within torrent titles, which **will prevent a download if found** (No delimiters or flags) (Optional). 
    * `webhooks [list]` - **List of strings** with the `name` values from `webhooks.json` that will be notified when a torrent file downloads (Optional).
  * `previous_hash [str]` - Previous hash value of most recent subscription fetch. This value is automatically updated for each subscription by the watcher.

> Use [this online Python script](https://onlinegdb.com/hsnOWQY6W) to create a custom JSON string for the `subscriptions.json` file.

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

> Visit the [nyaa-watcher Wiki](https://github.com/resort-io/nyaa-watcher/wiki#example-subscriptionsjson) for more information.

> See [Regular Expressions](#regular-expressions) below for more information on patterns.

### `webhooks.json`

Contains the information for the Discord webhooks and notification customization.

> #### Important Notes
> 
> * Multiple `webhooks.json` entries can use the same `url` value.

* `name [str]` - **Name of the webhook** (This is the value used in the `webhooks` property in `watchlist.json`).
* `url [str]` - **URL of the Discord webhook**.
* `notifications [dict]` - Customization for the notification.
  * `title [str]` - **Custom title** of the Discord notification. **Leave blank for default message**.
  * `description [str]` - **Custom description** of the Discord notification. **Leave blank for no message**.
  * `show_category [int]` - (0 to 6) **Nyaa category** for the torrent.
  * `show_downloads [int]` - (0 to 6) **Number of downloads** for the torrent.
  * `show_leechers [int]` - (0 to 6) **Number of leechers** for the torrent.
  * `show_published [int]` - (0 to 6) **Date and time** the torrent was published. 
  * `show_seeders [int]` - (0 to 6) **Number of seeders** for the torrent.
  * `show_size [int]` - (0 to 6) **Size of the torrent**.

> Use [this online Python script](https://onlinegdb.com/3o648M3tp) to create a custom JSON string for the `webhooks.json` file.

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

> Visit the [nyaa-watcher Wiki](https://github.com/resort-io/nyaa-watcher/wiki#example-webhooksjson) for more information.

### Torrent Info Tokens

Use tokens to insert torrent information into the `title` and `description` values:

* `$category` - **Nyaa category** for the torrent (e.g., *Anime - English-translated*).
* `$downloads` - **Number of downloads** for the torrent.
* `$leechers` - **Number of leechers** for the torrent.
* `$published` - **Date and time** the torrent was published (e.g., *Fri, 20 Apr 2023 20:47*).
* `$seeders` - **Number of seeders** for the torrent.
* `$size` - **Size of the torrent** (e.g., *178.2 MiB*).
* `$title` - **Title of the torrent**.
* `$uploader` - **Nyaa username** of the uploader.
* `$watchlist` - **Name of the watchlist** entry (Defaults to *Unknown Watchlist*).
* `$webhook` - **Name of the webhook**.

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

## Regular Expressions

Below are examples of regular expressions that can be modified for your needs.

Titles with the `00` format may contain the words ***720p*** or ***1080p***, which may interfere with searching,
so you may want to use a `regex` value (or combination with a `tags` value) that contains the **series title and the numbering pattern**.

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
