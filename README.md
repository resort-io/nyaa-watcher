[![Nyaa Watcher Banner](https://raw.githubusercontent.com/resort-io/assets/main/nyaa-watcher/img/banner.png)](https://github.com/resort-io/nyaa-watcher)

[![Nyaa Watcher GitHub Repository](https://img.shields.io/static/v1.svg?color=0085ff&labelColor=555555&logoColor=ffffff&style=for-the-badge&label=github&message=nyaa-watcher&logo=github)](https://github.com/resort-io/nyaa-watcher "GitHub Page")
[![Latest GitHub Release](https://img.shields.io/github/v/release/resort-io/nyaa-watcher?color=0085ff&logo=github&style=for-the-badge)](https://github.com/resort-io/nyaa-watcher/releases "Latest GitHub release")
[![Latest Docker Image Tags](https://img.shields.io/docker/v/resortdocker/nyaa-watcher?color=0085ff&logo=docker&logoColor=white&style=for-the-badge)](https://hub.docker.com/r/resortdocker/nyaa-watcher/tags "Latest Docker Image")
![Docker Image Pulls](https://img.shields.io/docker/pulls/resortdocker/nyaa-watcher?color=0085ff&label=pulls&logo=docker&logoColor=white&style=for-the-badge "Docker Image Pulls")

## Features

* Monitors a Nyaa user's RSS feed and downloads torrent files based upon substrings and/or regular expressions.
* Notifies Discord channels via webhooks when a torrent file is downloaded.

## Usage

### [docker cli](https://docs.docker.com/engine/reference/commandline/cli/)

```docker
docker run
  --name=nyaa-watcher
  -v /path/to/torrent-client/watch:/downloads
  -v /path/to/appdata/nyaa-watcher:/watcher
  --restart unless-stopped
  resortdocker/nyaa-watcher:latest
```

### Parameters

The syntax for the volume parameter is `<host>:<container>`. See the [setup documentation](https://github.com/resort-io/nyaa-watcher/blob/main/SETUP.md) for more information.

| Parameter      | Description                                                                    |
|----------------|--------------------------------------------------------------------------------|
| `-v /watch`    | Watch directory for your torrent client.                                       |
| `-v /watcher`  | Directory for Nyaa Watcher files.                                              |
| `-e LOG_LEVEL` | Log information level (Optional). `INFO` (default) or `DEBUG`                  |
| `-e SHOW_TIPS` | Show tips in the log from the watcher (Optional) . `true` (default) or `false` |

## Issues

If you encounter any bugs or issues, please make a report [here](https://github.com/resort-io/nyaa-watcher/issues/new/choose).