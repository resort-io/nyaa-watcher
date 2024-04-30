[![Nyaa Watcher Banner](https://raw.githubusercontent.com/resort-io/assets/main/nyaa-watcher/img/banner.png)](https://github.com/resort-io/nyaa-watcher)

[![Nyaa Watcher GitHub Repository](https://img.shields.io/static/v1.svg?color=0085ff&labelColor=555555&logoColor=ffffff&style=for-the-badge&label=github&message=nyaa-watcher&logo=github)](https://github.com/resort-io/nyaa-watcher "GitHub Repository")
[![Latest GitHub Release](https://img.shields.io/github/v/release/resort-io/nyaa-watcher?color=0085ff&logo=github&style=for-the-badge)](https://github.com/resort-io/nyaa-watcher/releases "Latest GitHub release")
[![Latest Docker Image Tags](https://img.shields.io/docker/v/resortdocker/nyaa-watcher?color=0085ff&logo=docker&logoColor=white&style=for-the-badge)](https://hub.docker.com/r/resortdocker/nyaa-watcher/tags "Latest Docker Image")
![Docker Image Pulls](https://img.shields.io/docker/pulls/resortdocker/nyaa-watcher?color=0085ff&label=pulls&logo=docker&logoColor=white&style=for-the-badge "Docker Image Pulls")

## Features

* Monitors multiple Nyaa users feeds and downloads torrent files based upon tags and/or regular expressions.
* Notifies Discord channels via webhooks when a torrent file is downloaded.

## Usage

See the [setup documentation](./SETUP.md) or [nyaa-watcher Wiki pages](https://github.com/resort-io/nyaa-watcher/wiki) for more information on Getting Started.

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

The syntax for the volume parameter is `<host>:<container>`. See the [nyaa-watcher Docker Wiki](https://github.com/resort-io/nyaa-watcher/wiki/Docker) for more information.

| Parameter       | Description                                                       |
|-----------------|-------------------------------------------------------------------|
| `-v /downloads` | Directory for downloaded torrent files.                           |
| `-v /watcher`   | Directory for watcher JSON files.                                 |

## Changelog

Changes for each release are listed in the [changelog](./CHANGELOG.md) file.

## Issues

If you encounter any bugs or issues, please make a report [here](https://github.com/resort-io/nyaa-watcher/issues/new/choose).