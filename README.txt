CLOUDIE — DISCORD BOT

Package contents
- bot.py: Main bot source (single-file bot; ai.py is not required)
- token.txt: Add your Discord bot token here
- requirements.txt: Python dependencies
- JSON files: Persistent settings/data files used by the bot
- cloudie_branding.png: Matching Cloudie banner + avatar concept

SETUP
1. Use Python 3.10 or newer.
2. Install dependencies: pip install -r requirements.txt
3. Open token.txt and replace PUT_YOUR_DISCORD_BOT_TOKEN_HERE with your bot token.
4. Enable the required privileged intents (Message Content and Server Members) in the Discord Developer Portal.
5. Run: python bot.py

BRANDING
The bot's embeds and visible branding use Cloudie with a soft lavender/pastel accent.
The Greet feature is exposed as /greet and the prefix command !greet. Legacy prefix aliases
!welcome, !setwelcome, and !welcomeconfig are retained for compatibility. Existing stored
welcome_config.json data is still used so old settings are not discarded.

IMPORTANT
- Never share token.txt or upload your real token publicly.
- Change the bot's actual Discord username/avatar/banner separately in the Discord Developer
  Portal / bot profile; source code cannot change the account-level bot name.
- Review permissions and test moderation/protection settings in a private test server first.
- This package does not include ai.py.


LAVALINK MUSIC CONFIG
- Public Lavalink v4 nodes are listed in lavalink_nodes.json.
- Cloudie reads this file at startup and attempts each node independently.
- If a public node is offline, the bot logs the failure and tries the next one.
- Public nodes are community-operated; uptime, speed, and credentials can change.
- Do not use public nodes for private or sensitive data. Prefer a node you control
  for dependable production use.
- The bot uses Wavelink 3.x, which supports Lavalink v4.


LIVE MUSIC EMBED
- Lavalink playback creates one Cloudie Now Playing panel per server.
- The panel displays artwork, title, artist, playback status and a progress bar.
- The same panel refreshes every 10 seconds and updates when a new Lavalink track starts.
- Pause, Resume, Skip and Stop controls refresh or stop the live panel.
- The panel is a Discord message; it cannot animate continuously every second because
  Discord message edits are rate-limited. Progress updates every 10 seconds.
- FFmpeg fallback and slash-command FFmpeg playback may show their existing static
  embed; the live progress panel currently targets Wavelink/Lavalink playback.
