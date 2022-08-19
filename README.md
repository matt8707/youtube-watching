# youtube-watching

A containerized flask app using [yt-dlp](https://github.com/yt-dlp/yt-dlp) to get the latest video from your YouTube watch history. This is as a workaround for YouTube Data API v3 deprecating `watchHistory`.

```bash
curl http://127.0.0.1:5678
```

```json
{
    "channel": "Bad Friends",
    "title": "Bobby's Bank Heist | Ep 129 | Bad Friends",
    "video_id": "7bT2zdzWAM4",
    "duration_string": "1:16:48",
    "thumbnail": "https://i.ytimg.com/vi/7bT2zdzWAM4/hqdefault.jpg",
    "original_url": "https://www.youtube.com/watch?v=7bT2zdzWAM4"
}
```

## Cookies

To authenticate with youtube, you need to set a HTTP Cookie File.

> "In order to extract cookies from browser use any conforming browser extension for exporting cookies. For example, [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid/) (for Chrome) or [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) (for Firefox)".

[https://github.com/ytdl-org/youtube-dl#how-do-i-pass-cookies-to-youtube-dl](https://github.com/ytdl-org/youtube-dl#how-do-i-pass-cookies-to-youtube-dl)

## Install

Pull and run with docker-compose.

```bash
cd docker-compose && \
  docker-compose up -d youtube-watching
```

```yaml
version: '3'
services:
  youtube-watching:
    container_name: youtube-watching
    image: ghcr.io/matt8707/youtube-watching
    volumes:
      - /volume1/docker/youtube-watching/config:/youtube-watching/config/
    environment:
      - COOKIE=./config/youtube.com_cookies.txt
    network_mode: bridge
    ports:
      - 5678:5678
    restart: always
```

## Build

You can also build the image with docker-compose.

```bash
cd docker-compose && \
  docker-compose up -d --build youtube-watching
```

```yaml
version: '3'
services:
  youtube-watching:
    container_name: youtube-watching
    build:
      context: /volume1/docker/youtube-watching/
      dockerfile: /volume1/docker/youtube-watching/Dockerfile
    volumes:
      - /volume1/docker/youtube-watching/config:/youtube-watching/config/
    environment:
      - COOKIE=./config/youtube.com_cookies.txt
    network_mode: bridge
    ports:
      - 5678:5678
    restart: always
```

## Home Assistant

The "YouTube" Apple TV app doesn't expose artwork through AirPlay, so the Home Assistant `apple_tv` integration can't show an `entity_picture`. This is an example to get the thumbnail.

```yaml
rest:
  - resource: http://192.168.1.241:5678
    sensor:
      name: youtube_watching
      value_template: >
        {% set video_id = value_json.video_id %}
        https://img.youtube.com/vi/{{video_id}}/maxresdefault.jpg
      json_attributes:
        - channel
        - title
        - video_id
        - duration_string
        - thumbnail
        - original_url
    scan_interval: 86400

automation:
  - alias: update_youtube_watching_thumbnail
    id: '1781428593188'
    mode: single
    max_exceeded: silent
    variables:
      ytw: >
        sensor.youtube_watching
    trigger:
      platform: state
      entity_id:
        - media_player.vardagsrum
        - media_player.sovrum
      to: playing
    condition: >
      {{ is_state_attr(trigger.entity_id, 'app_id', 'com.google.ios.youtube') and
      state_attr(trigger.entity_id, 'media_title') != state_attr(ytw, 'title') }}
    action:
      - service: homeassistant.update_entity
        target:
          entity_id: >
            {{ ytw }}
```
