# Cloudie Discord Bot

Cloudie is a discord.py 2.x bot with moderation, protection, greet, ticket,
autoresponder and Lavalink/Wavelink music features.

## Requirements

- Python 3.10–3.12 recommended
- FFmpeg installed and available on PATH (only needed by the legacy yt-dlp fallback)
- A reachable Lavalink v4 server for music
- Discord bot with Server Members, Message Content and Voice States intents enabled

## Install

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows: .venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Put your bot token in `token.txt` (one line), or set `DISCORD_TOKEN` in the environment.
Do not upload a real token or Lavalink password to a public repository.

## Lavalink

Edit `lavalink_nodes.json` and provide your own Lavalink v4 node details:

```json
[
  {
    "identifier": "primary",
    "host": "your-lavalink-host.example",
    "port": 443,
    "password": "YOUR_LAVALINK_PASSWORD",
    "secure": true,
    "version": "v4"
  }
]
```

The public nodes present in the supplied archive are retained as configuration examples;
public nodes can be offline, rate-limited, or change credentials without notice. A self-hosted
or trusted node is recommended. Wavelink connects during the real discord.py `setup_hook`.

## Start

```bash
python bot.py
```

Prefix: `!`

## Music commands

- `!play <query>`
- `!pause`, `!resume`, `!skip`, `!stop`
- `!queue`, `!nowplaying`
- `!volume <0-100>`
- `!autoplay`, `!loop [on/off]`
- `!247` — join the voice channel you want Cloudie to remain in, then toggle 24/7.
- The persistent Now Playing panel has Pause, Resume, Skip, Stop, Queue, Autoplay,
  24/7 and Filters controls.

The Filters menu sends real Wavelink filter requests to the current Lavalink player.
A filter may fail if the selected Lavalink node/backend does not support that filter payload.

## 24/7 persistence

`twentyfour.json` stores one independent entry per guild:

```json
{
  "123456789012345678": {
    "enabled": true,
    "channel_id": 123456789012345678
  }
}
```

When 24/7 is enabled, Cloudie first joins the member's current voice channel and then
atomically writes the guild ID and voice channel ID. On startup, after Discord is ready,
Cloudie loads every enabled record and reconnects each guild independently. The reconnect
worker checks the guild, channel and Connect/Speak permissions, avoids a second connection
if the guild is already connected, serializes attempts per guild, and uses bounded exponential
backoff. Unexpected voice disconnects schedule a reconnect. Turning 24/7 off removes that
guild's record; other guilds remain untouched.

Old Cloudie `twentyfour.json` files containing only `true`/`false` values are migrated.
A legacy `true` value has no channel ID, so Cloudie deliberately does not guess a channel;
re-enable 24/7 from the desired voice channel to save it.

`music_panels.json` stores the channel/message IDs for each server's Now Playing panel.
The bot edits the existing panel and only creates a replacement if the saved message no
longer exists or cannot be accessed.

## Existing configuration files

The original JSON files for AntiNuke, AutoMod, punishments, greet, tickets, autoresponder,
bad words, nickname words, autoplay and Lavalink nodes are retained. Back them up before
upgrading or moving hosts.

## Testing notes

Static Python compilation and archive integrity checks are part of this rebuild. A live
Discord gateway, voice connection and Lavalink node are external services; those cannot
be truthfully marked as runtime-tested from this build environment. Test in a private
Discord server before deploying broadly.
