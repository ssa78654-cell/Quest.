import asyncio
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except:
    pass

import discord
from discord import app_commands
from discord.ext import commands
from collections import defaultdict, deque
from datetime import timedelta
import time
import random
import os
import sys
import re
import json
import gc
import platform
import yt_dlp
import wavelink

try:
    TOKEN = open("token.txt").read().strip()
except FileNotFoundError:
    TOKEN = "PUT_YOUR_BOT_TOKEN_HERE_IN_token.txt_FILE"
    print("ERROR: token.txt not found! Create token.txt with your bot token inside.")

PREFIX = "!"
OWNER_ID = 1476134045057417368
START_TIME = time.time()

def get_prefix(bot, message):
    if getattr(message.author, "id", None) == OWNER_ID:
        return [PREFIX, ""]
    return PREFIX

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.bans = True
intents.guild_messages = True
intents.guild_reactions = True

bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=None,
    chunk_guilds_at_startup=False,
    member_cache_flags=discord.MemberCacheFlags(voice=True, joined=True),
    max_messages=1000,
    heartbeat_timeout=30.0
)

# ===================== DATA STORAGE =====================
warnings = defaultdict(list)
welcome_enabled = defaultdict(lambda: True)
welcome_channels = {}
welcome_config = defaultdict(lambda: {
    "enabled": True,
    "channel": None,
    "message": "Greet {user} to **{server}**! You are member #{count} 🎉",
    "embed_enabled": True,
    "embed_title": "Greet to {server}!",
    "embed_description": "Hey {user}, welcome to **{server}**!\n\nYou are our **{count}th** member.\nPlease read the rules and enjoy your stay!",
    "embed_color": 0x00FF00,
    "embed_thumbnail": True,
    "embed_image": None
})
twentyfour_seven = defaultdict(bool)
ticket_counter = defaultdict(int)
ticket_config = defaultdict(lambda: {
    "embed_title": "Support Ticket",
    "embed_description": "Click the button below to create a support ticket.\nOur staff will assist you shortly.",
    "embed_color": 0x00FF00,
    "button_label": "Create Ticket"
})
automod_config = defaultdict(lambda: {
    "invite": True, "spam": True, "caps": True, "everyone": True, 
    "badwords": True, "fban": True, "nickban": True,
    "antinuke": False, "antispam": True, "anticaps": True, 
    "antibadword": True, "antilink": True, "antiraid": False,
    "antieveryone": True, "antiinvite": True
})
automod_punishment = defaultdict(lambda: {
    "invite": "delete", "spam": "mute", "caps": "warn", "everyone": "delete",
    "badwords": "delete", "fban": "ban", "nickban": "rename",
    "antinuke": "ban", "antispam": "mute", "anticaps": "warn",
    "antibadword": "delete", "antilink": "delete", "antiraid": "ban",
    "antieveryone": "delete", "antiinvite": "delete"
})
antinuke_config = defaultdict(lambda: {
    "enabled": False,
    "punishment": "ban",
    "whitelist": [],
    "log_channel": None,
    "protect_channels": True,
    "protect_roles": True,
    "protect_bans": True,
    "protect_kicks": True,
    "protect_bots": True
})
autoplay_state = defaultdict(bool)
autoplay_history = defaultdict(set)
last_text_channel = {}
last_requester = {}
BAD_WORDS = ["fuck", "bitch", "nigga", "nigger"]
NICK_BAN_WORDS = ["admin", "moderator", "owner"]
AUTORESPONDER = {}
spam_tracker = defaultdict(lambda: deque(maxlen=10))
recent_actions = defaultdict(list)

try:
    if os.path.exists("badwords.json"):
        BAD_WORDS = json.load(open("badwords.json"))
    if os.path.exists("nickbanwords.json"):
        NICK_BAN_WORDS = json.load(open("nickbanwords.json"))
    if os.path.exists("autoresponder.json"):
        AUTORESPONDER = json.load(open("autoresponder.json"))
    if os.path.exists("twentyfour.json"):
        data = json.load(open("twentyfour.json"))
        for k,v in data.items():
            twentyfour_seven[int(k)] = v
    if os.path.exists("autoplay.json"):
        data = json.load(open("autoplay.json"))
        for k,v in data.items():
            autoplay_state[int(k)] = v
    if os.path.exists("welcome_config.json"):
        data = json.load(open("welcome_config.json"))
        for k,v in data.items():
            welcome_config[int(k)].update(v)
            welcome_channels[int(k)] = v.get("channel")
    if os.path.exists("automod_config.json"):
        data = json.load(open("automod_config.json"))
        for k,v in data.items():
            automod_config[int(k)].update(v)
    if os.path.exists("automod_punishment.json"):
        data = json.load(open("automod_punishment.json"))
        for k,v in data.items():
            automod_punishment[int(k)].update(v)
    if os.path.exists("antinuke_config.json"):
        data = json.load(open("antinuke_config.json"))
        for k,v in data.items():
            antinuke_config[int(k)].update(v)
    if os.path.exists("ticket_config.json"):
        data = json.load(open("ticket_config.json"))
        for k,v in data.items():
            ticket_config[int(k)].update(v)
except: pass

def save_badwords():
    try: json.dump(BAD_WORDS, open("badwords.json","w"))
    except: pass
def save_nickban():
    try: json.dump(NICK_BAN_WORDS, open("nickbanwords.json","w"))
    except: pass
def save_autoresponder():
    try: json.dump(AUTORESPONDER, open("autoresponder.json","w"))
    except: pass
def save_247():
    try: json.dump({str(k):v for k,v in twentyfour_seven.items()}, open("twentyfour.json","w"))
    except: pass
def save_autoplay():
    try: json.dump({str(k):v for k,v in autoplay_state.items()}, open("autoplay.json","w"))
    except: pass
def save_welcome_config():
    try: 
        data = {str(k): dict(v) for k,v in welcome_config.items()}
        json.dump(data, open("welcome_config.json","w"), indent=2)
    except: pass
def save_automod_config():
    try: 
        data = {str(k): dict(v) for k,v in automod_config.items()}
        json.dump(data, open("automod_config.json","w"), indent=2)
    except: pass
def save_automod_punishment():
    try: 
        data = {str(k): dict(v) for k,v in automod_punishment.items()}
        json.dump(data, open("automod_punishment.json","w"), indent=2)
    except: pass
def save_antinuke_config():
    try: 
        data = {str(k): dict(v) for k,v in antinuke_config.items()}
        json.dump(data, open("antinuke_config.json","w"), indent=2)
    except: pass
def save_ticket_config():
    try: 
        data = {str(k): dict(v) for k,v in ticket_config.items()}
        json.dump(data, open("ticket_config.json","w"), indent=2)
    except: pass

# ===================== FAST SEARCH & LAVALINK NODES =====================
YTDL_OPTS = {
    'format': 'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best',
    'quiet': True, 'no_warnings': True, 'noplaylist': False,
    'extract_flat': False, 'nocheckcertificate': True,
    'ignoreerrors': True, 'default_search': 'ytsearch10',
    'source_address': '0.0.0.0',
    'extractor_args': {'youtube': {'player_client': ['android','web','mweb']}},
    'retries': 10, 'fragment_retries': 10, 'concurrent_fragment_downloads': 4,
    'http_headers': {'User-Agent': 'Mozilla/5.0'}
}
FFMPEG_OPTS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -analyzeduration 0 -probesize 512k -fflags +nobuffer -flags low_delay',
    'options': '-vn -ar 48000 -ac 2 -b:a 192k -bufsize 512k -application lowdelay'
}
ytdl = yt_dlp.YoutubeDL(YTDL_OPTS)
ffmpeg_queue = {}
ffmpeg_now_playing = {}

def get_queue(guild_id):
    if guild_id not in ffmpeg_queue:
        ffmpeg_queue[guild_id] = []
    return ffmpeg_queue[guild_id]

# Public Lavalink v4 nodes are configured in lavalink_nodes.json.
# Public nodes can go offline or change credentials without notice.
def load_lavalink_configs():
    try:
        with open("lavalink_nodes.json", "r", encoding="utf-8") as file:
            configs = json.load(file)
        if not isinstance(configs, list):
            raise ValueError("lavalink_nodes.json must contain a JSON list")
        valid = []
        for item in configs:
            if not isinstance(item, dict):
                continue
            host = str(item.get("host", "")).strip()
            password = str(item.get("password", "")).strip()
            port = int(item.get("port", 443))
            secure = bool(item.get("secure", True))
            version = str(item.get("version", "v4")).lower()
            identifier = str(item.get("identifier", host)).strip()
            if host and password and 1 <= port <= 65535 and version == "v4":
                scheme = "https" if secure else "http"
                valid.append({"uri": f"{scheme}://{host}:{port}", "password": password,
                              "identifier": identifier or host})
        return valid
    except Exception as error:
        print(f"[Cloudie Lavalink] Could not read lavalink_nodes.json: {error}")
        return []

NODE_CONFIGS = load_lavalink_configs()

def get_after_callback(guild_id):
    def after(error):
        if error:
            print(f"Player error: {error}")
        try:
            loop = bot.loop if hasattr(bot, 'loop') else asyncio.get_event_loop()
            coro = play_next_ffmpeg(guild_id)
            asyncio.run_coroutine_threadsafe(coro, loop)
        except Exception as ex:
            print(f"After error: {ex}")
    return after

async def play_next_ffmpeg(guild_id):
    queue = get_queue(guild_id)
    guild = bot.get_guild(guild_id)
    if not guild: return
    vc = guild.voice_client
    if not vc: return
    channel_id = last_text_channel.get(guild_id)
    text_channel = bot.get_channel(channel_id) if channel_id else None
    next_data = None
    if queue:
        next_data = queue.pop(0)
        if not next_data.get('url'):
            try:
                loop = asyncio.get_event_loop()
                webpage = next_data.get('webpage_url')
                if webpage:
                    fresh = await loop.run_in_executor(None, lambda: ytdl.extract_info(webpage, download=False))
                    next_data = fresh
            except: pass
    elif autoplay_state.get(guild_id, False) and True:  # Fixed autoplay always check
        last = ffmpeg_now_playing.get(guild_id)
        if last:
            base_title = last.get('title','')
            uploader = last.get('uploader','')
            search_query = f"{uploader} {base_title.split('(')[0].split('[')[0].strip()} mix"
            try:
                loop = asyncio.get_event_loop()
                search_data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch5:{search_query}", download=False))
                entries = search_data.get('entries', [])
                for entry in entries:
                    if entry.get('title','').lower() in autoplay_history[guild_id]: continue
                    if is_same_song(base_title, entry.get('title','')): continue
                    webpage = entry.get('webpage_url')
                    if webpage:
                        full = await loop.run_in_executor(None, lambda: ytdl.extract_info(webpage, download=False))
                        next_data = full
                        break
                if next_data:
                    autoplay_history[guild_id].add(next_data.get('title','').lower())
                    if len(autoplay_history[guild_id]) > 50:
                        autoplay_history[guild_id] = set(list(autoplay_history[guild_id])[-30:])
            except Exception as e:
                print(f"Autoplay failed: {e}")
                return
    else:
        if not twentyfour_seven.get(guild_id, False):
            try:
                await asyncio.sleep(2)
                if not get_queue(guild_id):
                    await vc.disconnect()
                    try: await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"/help • {len(bot.guilds)} servers"))
                    except: pass
            except: pass
        return
    if not next_data: return
    audio_url = next_data.get('url')
    if not audio_url:
        try:
            loop = asyncio.get_event_loop()
            webpage = next_data.get('webpage_url')
            if webpage:
                fresh = await loop.run_in_executor(None, lambda: ytdl.extract_info(webpage, download=False))
                audio_url = fresh.get('url')
                next_data = fresh
        except: pass
    if not audio_url:
        await play_next_ffmpeg(guild_id)
        return
    ffmpeg_now_playing[guild_id] = next_data
    source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTS)
    player = YTDLSource(source, data=next_data)
    try: vc.play(player, after=get_after_callback(guild_id))
    except: return
    try: await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=next_data.get('title','')[:30]))
    except: pass
    if text_channel:
        try:
            is_auto = autoplay_state.get(guild_id, False) and not queue
            title_text = "🔁 Autoplay - Now Playing" if is_auto else "🎧 Now Playing - Outside"
            embed = discord.Embed(title=title_text, description=f"**{next_data.get('title')}**\n\n▶️ Song is playing inside VC, showing outside in chat!", color=0x00FF00 if is_auto else 0xE7D6FF)
            if next_data.get('thumbnail'): 
                embed.set_thumbnail(url=next_data.get('thumbnail'))
                embed.set_image(url=next_data.get('thumbnail'))
            uploader = next_data.get('uploader','Unknown')
            duration = next_data.get('duration',0)
            embed.add_field(name="Uploader", value=uploader[:50], inline=True)
            if duration:
                embed.add_field(name="Duration", value=f"{duration//60}:{duration%60:02d}", inline=True)
            embed.add_field(name="Autoplay", value="ON 🔁" if autoplay_state.get(guild_id) else "OFF", inline=True)
            req = last_requester.get(guild_id)
            if req:
                embed.set_footer(text=f"Requested by {req} | Cloudie Premium | Showing Outside Chat", icon_url=req.display_avatar.url if hasattr(req, 'display_avatar') else None)
            else:
                embed.set_footer(text="Cloudie • Premium Bot 🎧 | Playing Outside Display")
            await text_channel.send(embed=embed, view=MusicView())
        except Exception as e:
            print(f"Outside embed error: {e}")

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.8):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('webpage_url') or data.get('url')
        self.thumbnail = data.get('thumbnail')
        self.duration = data.get('duration', 0)
        self.uploader = data.get('uploader', 'Unknown')
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTS), data=data)

def normalize_words(title):
    title = title.lower()
    title = re.sub(r'\(.*?\)|\(.*?\)', ' ', title)
    title = re.sub(r'lyrics|official|video|audio|song|new|trending|reel|2024|2025|2026|2023|4k|8k|hd|#\w+', ' ', title)
    title = re.sub(r'[^a-z0-9 ]', ' ', title)
    words = [w.strip() for w in title.split() if len(w.strip()) > 2]
    return set(words)

def is_same_song(t1, t2):
    w1 = normalize_words(t1)
    w2 = normalize_words(t2)
    if not w1 or not w2: return False
    common = w1.intersection(w2)
    if not common: return False
    overlap = len(common) / min(len(w1), len(w2)) if min(len(w1), len(w2)) > 0 else 0
    if overlap >= 0.5: return True
    if len(w1) <= 2 or len(w2) <= 2:
        if len(common) >= 1: return True
    return False

async def dm_user(member, action, server, reason, duration_text, moderator):
    if member.bot:
        return False, None
    guild = server if isinstance(server, discord.Guild) else None
    server_name = guild.name if guild else str(server)
    server_icon = guild.icon.url if guild and guild.icon else bot.user.display_avatar.url if bot.user.display_avatar else None
    bot_icon = bot.user.display_avatar.url if bot.user.display_avatar else None
    if action == "Banned":
        color, title, emoji = 0xFF0000, "You have been Banned!", "🔨"
    elif action == "Kicked":
        color, title, emoji = 0xFF6B00, "You have been Kicked!", "👢"
    elif action == "Muted":
        color, title, emoji = 0xFFA500, "You have been Muted!", "🔇"
    elif action == "Warned":
        color, title, emoji = 0xFFFF00, "You have been Warned!", "⚠️"
    else:
        color, title, emoji = 0xC9A7F5, f"You have been {action}!", "⚠️"
    embed = discord.Embed(title=f"{emoji} {title}", description=f"You received a moderation action in {server_name}", color=color)
    if server_icon:
        embed.set_author(name=f"{server_name}", icon_url=server_icon)
        embed.set_thumbnail(url=server_icon)
    if bot_icon:
        embed.set_footer(text=f"{server_name}", icon_url=bot_icon)
    embed.add_field(name="Server", value=f"{server_name}", inline=False)
    embed.add_field(name="Action", value=f"{action}", inline=True)
    embed.add_field(name="Moderator", value=f"{moderator}", inline=True)
    if duration_text:
        embed.add_field(name="Duration", value=f"{duration_text}", inline=True)
    embed.add_field(name="Reason", value=f"{reason}", inline=False)
    embed.add_field(name="What to do?", value="If you think this was a mistake, contact the server moderators.", inline=False)
    embed.timestamp = discord.utils.utcnow()
    try:
        await member.send(embed=embed)
        return True, embed
    except discord.Forbidden:
        try:
            await member.send(f"{title} in {server_name}\nServer: {server_name}\nAction: {action}\nReason: {reason}\nModerator: {moderator}")
            return True, embed
        except:
            return False, embed
    except:
        try:
            await member.send(f"You have been {action} in {server_name}\nReason: {reason}")
            return True, embed
        except:
            return False, embed

def is_owner(ctx): return ctx.author.id == OWNER_ID
def is_staff(m): return m.guild_permissions.administrator or m.guild_permissions.manage_guild or m.guild_permissions.manage_messages or m.guild_permissions.ban_members

async def apply_punishment(member, guild, feature, reason):
    punishment = automod_punishment[guild.id].get(feature, "delete")
    try:
        if punishment == "ban":
            await member.ban(reason=f"AutoMod {feature}: {reason}")
        elif punishment == "kick":
            await member.kick(reason=f"AutoMod {feature}: {reason}")
        elif punishment == "mute":
            until = discord.utils.utcnow() + timedelta(minutes=10)
            await member.timeout(until, reason=f"AutoMod {feature}: {reason}")
        elif punishment == "warn":
            warnings[member.id].append({"reason": f"AutoMod {feature}: {reason}", "mod": bot.user.id, "time": time.time()})
    except: pass

# ===================== VIEWS =====================

# ===================== CLOUDIE LIVE MUSIC PANEL =====================
live_music_messages = {}
live_music_tasks = {}
live_music_track_ids = {}

def _live_time(ms):
    seconds = max(0, int(ms or 0) // 1000)
    return f"{seconds // 60}:{seconds % 60:02d}"

def _live_music_embed(player, guild_id):
    track = getattr(player, "current", None)
    if not track:
        return discord.Embed(
            title="☁️ Cloudie • Music Player",
            description="Nothing is playing right now.",
            color=0xDCCBFA
        )
    duration = int(getattr(track, "length", 0) or 0)
    position = int(getattr(player, "position", 0) or 0)
    paused = bool(getattr(player, "paused", False))
    if duration > 0:
        ratio = min(1.0, position / duration)
        filled = min(16, max(0, int(ratio * 16)))
        bar = "▰" * filled + "▱" * (16 - filled)
        progress = f"`{_live_time(position)}` {bar} `{_live_time(duration)}`"
    else:
        progress = "`LIVE`"
    status = "⏸ Paused" if paused else "▶ Playing"
    title = str(getattr(track, "title", "Unknown track"))[:240]
    artist = str(getattr(track, "author", "Unknown artist"))[:100]
    uri = getattr(track, "uri", None)
    description = f"**[{title}]({uri})**" if uri else f"**{title}**"
    embed = discord.Embed(
        title="☁️ Cloudie • Now Playing",
        description=f"{description}\n**Artist:** {artist}\n\n{progress}",
        color=0xDCCBFA
    )
    artwork = getattr(track, "artwork", None)
    if artwork:
        try:
            embed.set_thumbnail(url=artwork)
        except Exception:
            pass
    embed.add_field(name="Status", value=status, inline=True)
    embed.add_field(name="Autoplay", value="On" if autoplay_state.get(guild_id, False) else "Off", inline=True)
    embed.add_field(name="24/7", value="On" if twentyfour_seven.get(guild_id, False) else "Off", inline=True)
    embed.set_footer(text="Cloudie • Live player • progress refreshes every 10 seconds")
    return embed

async def _refresh_live_music_panel(guild_id, player=None, channel=None):
    player = player or bot.voice_clients and next(
        (vc for vc in bot.voice_clients if vc.guild and vc.guild.id == guild_id), None
    )
    if not isinstance(player, wavelink.Player):
        return
    msg = live_music_messages.get(guild_id)
    embed = _live_music_embed(player, guild_id)
    if msg:
        try:
            await msg.edit(embed=embed, view=MusicView())
            return
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            live_music_messages.pop(guild_id, None)
    if channel is None:
        channel_id = last_text_channel.get(guild_id)
        channel = bot.get_channel(channel_id) if channel_id else None
    if channel:
        try:
            live_music_messages[guild_id] = await channel.send(embed=embed, view=MusicView())
        except discord.HTTPException as error:
            print(f"[Cloudie Live Music] Could not send panel: {error}")

async def _live_music_refresh_loop(guild_id):
    try:
        while True:
            await asyncio.sleep(10)
            guild = bot.get_guild(guild_id)
            player = guild.voice_client if guild else None
            if not isinstance(player, wavelink.Player) or not getattr(player, "current", None):
                break
            await _refresh_live_music_panel(guild_id, player=player)
    except asyncio.CancelledError:
        raise
    except Exception as error:
        print(f"[Cloudie Live Music] Refresh error in {guild_id}: {error}")
    finally:
        live_music_tasks.pop(guild_id, None)

async def _start_live_music_panel(guild_id, player, channel=None):
    await _refresh_live_music_panel(guild_id, player=player, channel=channel)
    old_task = live_music_tasks.get(guild_id)
    if old_task and not old_task.done():
        old_task.cancel()
    live_music_tasks[guild_id] = asyncio.create_task(_live_music_refresh_loop(guild_id))


class MusicView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Pause", style=discord.ButtonStyle.secondary, emoji="⏸️")
    async def pause_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing(): 
            vc.pause()
            await interaction.response.send_message("⏸️ Paused.", ephemeral=True)
            if isinstance(vc, wavelink.Player):
                await _refresh_live_music_panel(interaction.guild.id, player=vc)
        else: await interaction.response.send_message("Nothing playing inside VC", ephemeral=True)
    @discord.ui.button(label="Resume", style=discord.ButtonStyle.success, emoji="▶️")
    async def resume_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused(): 
            vc.resume()
            await interaction.response.send_message("▶️ Resumed.", ephemeral=True)
            if isinstance(vc, wavelink.Player):
                await _refresh_live_music_panel(interaction.guild.id, player=vc)
        else: await interaction.response.send_message("Not paused", ephemeral=True)
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary, emoji="⏭️")
    async def skip_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc: 
            vc.stop()
            await interaction.response.send_message("⏭️ Skipped.", ephemeral=True)
            if isinstance(vc, wavelink.Player):
                await _refresh_live_music_panel(interaction.guild.id, player=vc)
        else: await interaction.response.send_message("Not in VC", ephemeral=True)
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⏹️")
    async def stop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc:
            get_queue(interaction.guild.id).clear()
            vc.stop()
            await interaction.response.send_message("⏹️ Stopped and cleared queue", ephemeral=True)
            live_music_messages.pop(interaction.guild.id, None)
            task = live_music_tasks.pop(interaction.guild.id, None)
            if task and not task.done():
                task.cancel()
        else: await interaction.response.send_message("Not in VC", ephemeral=True)
    @discord.ui.button(label="Queue", style=discord.ButtonStyle.secondary, emoji="📜")
    async def queue_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(interaction.guild.id)
        if not q: await interaction.response.send_message("Queue empty", ephemeral=True)
        else:
            desc = "\n".join(f"{i+1}. {t.get('title','Unknown')[:45]}" for i,t in enumerate(q[:5]))
            embed = discord.Embed(title=f"Queue - {len(q)} songs - Showing Outside", description=desc, color=0xE7D6FF)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    @discord.ui.button(label="Autoplay", style=discord.ButtonStyle.secondary, emoji="🔁")
    async def autoplay_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = interaction.guild.id
        autoplay_state[gid] = not autoplay_state[gid]
        save_autoplay()
        status = "ON 🔁" if autoplay_state[gid] else "OFF"
        await interaction.response.send_message(f"🔁 Autoplay Fixed: {status} - When ON, after song ends next similar song will auto play and show outside in chat!", ephemeral=True)
    @discord.ui.button(label="24/7", emoji="🔒", style=discord.ButtonStyle.green, custom_id="music_247_v10")
    async def twentyfour_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = interaction.guild.id
        twentyfour_seven[gid] = not twentyfour_seven[gid]
        save_247()
        status = "ON" if twentyfour_seven[gid] else "OFF"
        await interaction.response.send_message(f"24/7: {status}", ephemeral=True)
    @discord.ui.button(label="Queue", emoji="📜", style=discord.ButtonStyle.gray, custom_id="music_queue_v10", row=1)
    async def queue_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await self._player(interaction)
        gid = interaction.guild.id
        items = []
        if player and hasattr(player, "queue"):
            try: items = list(player.queue)[:10]
            except Exception: items = []
            if not items:
                return await interaction.response.send_message("Queue empty.", ephemeral=True)
            desc = "\n".join(f"`{i}.` **{t.title[:40]}** - {t.author}" for i, t in enumerate(items, 1))
        else:
            items = get_queue(gid)[:10]
            if not items:
                return await interaction.response.send_message("Queue empty.", ephemeral=True)
            desc = "\n".join(f"`{i}.` **{t.get('title', 'Unknown')[:40]}** - {t.get('uploader', 'Unknown')}" for i, t in enumerate(items, 1))
        embed = discord.Embed(title="✦ Cloudie • Premium Queue", description=desc, color=0xC9A7F5)
        embed.set_footer(text="Cloudie • Premium Bot 🎧")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MentionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Invite", emoji="🔗", style=discord.ButtonStyle.gray, custom_id="invite_v9")
    async def invite_btn(self, interaction, button):
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
        await interaction.response.send_message(f"Invite: {invite_url}", ephemeral=True)

class HelpPaginator(discord.ui.View):
    def __init__(self, pages):
        super().__init__(timeout=120)
        self.pages = pages
        self.current = 0
    @discord.ui.button(label="FIRST", style=discord.ButtonStyle.green)
    async def first_btn(self, interaction, button):
        self.current = 0
        self.update_labels()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)
    @discord.ui.button(label="PREV", style=discord.ButtonStyle.green)
    async def prev_btn(self, interaction, button):
        if self.current > 0: self.current -= 1
        self.update_labels()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)
    @discord.ui.button(label="1/1", style=discord.ButtonStyle.gray, disabled=True)
    async def page_btn(self, interaction, button): pass
    @discord.ui.button(label="NEXT", style=discord.ButtonStyle.green)
    async def next_btn(self, interaction, button):
        if self.current < len(self.pages)-1: self.current += 1
        self.update_labels()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)
    @discord.ui.button(label="LAST", style=discord.ButtonStyle.green)
    async def last_btn(self, interaction, button):
        self.current = len(self.pages)-1
        self.update_labels()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)
    def update_labels(self):
        for child in self.children:
            if child.label and "/" in child.label:
                child.label = f"{self.current+1}/{len(self.pages)}"

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.blurple, custom_id="create_ticket_v9")
    async def create_ticket(self, interaction, button):
        guild = interaction.guild
        user = interaction.user
        ticket_counter[guild.id] += 1
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }
        for role in guild.roles:
            if role.permissions.administrator:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        try:
            channel = await guild.create_text_channel(name=f"ticket-{user.name[:10]}-{ticket_counter[guild.id]}", overwrites=overwrites, reason=f"Ticket by {user}")
            embed = discord.Embed(title=ticket_config[guild.id]["embed_title"], description=f"Hello {user.mention}\n{ticket_config[guild.id]['embed_description']}", color=ticket_config[guild.id]["embed_color"])
            await channel.send(f"{user.mention}", embed=embed)
            await interaction.response.send_message(f"Ticket: {channel.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed: {e}", ephemeral=True)

class AutomodView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=180)
        self.guild_id = guild_id
    
    @discord.ui.button(label="Toggle AntiNuke", emoji="💣", style=discord.ButtonStyle.red, row=0)
    async def antinuke_btn(self, interaction, button):
        cfg = antinuke_config[self.guild_id]
        cfg["enabled"] = not cfg["enabled"]
        save_antinuke_config()
        status = "ON" if cfg["enabled"] else "OFF"
        await interaction.response.send_message(f"AntiNuke: {status}", ephemeral=True)
    
    @discord.ui.button(label="Toggle AntiSpam", emoji="🚫", style=discord.ButtonStyle.blurple, row=0)
    async def antispam_btn(self, interaction, button):
        cfg = automod_config[self.guild_id]
        cfg["antispam"] = not cfg["antispam"]
        cfg["spam"] = cfg["antispam"]
        save_automod_config()
        status = "ON" if cfg["antispam"] else "OFF"
        await interaction.response.send_message(f"AntiSpam: {status}", ephemeral=True)
    
    @discord.ui.button(label="Toggle AntiCaps", emoji="🔠", style=discord.ButtonStyle.gray, row=0)
    async def anticaps_btn(self, interaction, button):
        cfg = automod_config[self.guild_id]
        cfg["anticaps"] = not cfg["anticaps"]
        cfg["caps"] = cfg["anticaps"]
        save_automod_config()
        status = "ON" if cfg["anticaps"] else "OFF"
        await interaction.response.send_message(f"AntiCaps: {status}", ephemeral=True)
    
    @discord.ui.button(label="Toggle AntiBadWord", emoji="🤬", style=discord.ButtonStyle.gray, row=0)
    async def antibadword_btn(self, interaction, button):
        cfg = automod_config[self.guild_id]
        cfg["antibadword"] = not cfg["antibadword"]
        cfg["badwords"] = cfg["antibadword"]
        save_automod_config()
        status = "ON" if cfg["antibadword"] else "OFF"
        await interaction.response.send_message(f"AntiBadWord: {status}", ephemeral=True)
    
    @discord.ui.button(label="Toggle AntiLink", emoji="🔗", style=discord.ButtonStyle.gray, row=1)
    async def antilink_btn(self, interaction, button):
        cfg = automod_config[self.guild_id]
        cfg["antilink"] = not cfg["antilink"]
        cfg["invite"] = cfg["antilink"]
        save_automod_config()
        status = "ON" if cfg["antilink"] else "OFF"
        await interaction.response.send_message(f"AntiLink/Invite: {status}", ephemeral=True)
    
    @discord.ui.button(label="Toggle AntiEveryone", emoji="📢", style=discord.ButtonStyle.gray, row=1)
    async def antieveryone_btn(self, interaction, button):
        cfg = automod_config[self.guild_id]
        cfg["antieveryone"] = not cfg["antieveryone"]
        cfg["everyone"] = cfg["antieveryone"]
        save_automod_config()
        status = "ON" if cfg["antieveryone"] else "OFF"
        await interaction.response.send_message(f"AntiEveryone: {status}", ephemeral=True)
    
    @discord.ui.button(label="Toggle AntiRaid", emoji="🛡️", style=discord.ButtonStyle.red, row=1)
    async def antiraid_btn(self, interaction, button):
        cfg = automod_config[self.guild_id]
        cfg["antiraid"] = not cfg["antiraid"]
        save_automod_config()
        status = "ON" if cfg["antiraid"] else "OFF"
        await interaction.response.send_message(f"AntiRaid: {status}", ephemeral=True)
    
    @discord.ui.button(label="View Config", emoji="⚙️", style=discord.ButtonStyle.green, row=2)
    async def view_btn(self, interaction, button):
        cfg = automod_config[self.guild_id]
        pun = automod_punishment[self.guild_id]
        anti = antinuke_config[self.guild_id]
        desc = f"**AntiNuke:** {'ON' if anti['enabled'] else 'OFF'} (Punishment: {anti['punishment']})\n"
        for k,v in cfg.items():
            if k not in ["fban", "nickban"]:
                desc += f"**{k}:** {'ON' if v else 'OFF'} (Punish: {pun.get(k, 'delete')})\n"
        embed = discord.Embed(title="🛡️ AutoMod Full Config", description=desc[:4000], color=0xC9A7F5)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    bot.add_view(MusicView())
    bot.add_view(MentionView())
    bot.add_view(TicketView())

@bot.event
async def on_wavelink_track_start(payload):
    player = getattr(payload, "player", None)
    if not player or not getattr(player, "guild", None):
        return
    guild_id = player.guild.id
    await _start_live_music_panel(guild_id, player)

@bot.event
async def on_wavelink_track_end(payload):
    player: wavelink.Player = payload.player
    if not player: return
    guild_id = player.guild.id if player.guild else None
    if not guild_id: return
    channel_id = last_text_channel.get(guild_id)
    channel = bot.get_channel(channel_id) if channel_id else None
    if player.queue.is_empty and autoplay_state.get(guild_id, False):
        try:
            current = payload.track
            if current:
                autoplay_history[guild_id].add(current.title.lower())
                query = f"{current.author} {current.title.split('(')[0]}"
                tracks = await wavelink.Playable.search(query)
                if tracks:
                    for track in tracks[:10]:
                        is_dup = False
                        for hist in autoplay_history[guild_id]:
                            if is_same_song(track.title, hist):
                                is_dup = True
                                break
                        if not is_dup:
                            await player.queue.put_wait(track)
                            autoplay_history[guild_id].add(track.title.lower())
                            if len(autoplay_history[guild_id]) > 50:
                                autoplay_history[guild_id] = set(list(autoplay_history[guild_id])[-30:])
                            break
        except: pass
    if not player.queue.is_empty:
        try:
            next_track = player.queue.get()
            await player.play(next_track)
            try:
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=next_track.title[:30]))
            except: pass
            if channel:
                if autoplay_state.get(guild_id, False):
                    embed = discord.Embed(title="Autoplay - Now Playing 🔁", description=f"**{next_track.title}**", color=0x00FF00)
                    embed.set_thumbnail(url=next_track.artwork or bot.user.display_avatar.url)
                    embed.add_field(name="Song", value=f"{next_track.title}", inline=False)
                    embed.add_field(name="Artist", value=f"{next_track.author}", inline=True)
                    await channel.send(content=f"Autoplay: {next_track.title} by {next_track.author}", embed=embed, view=MusicView())
                else:
                    embed = discord.Embed(title="Now Playing - Next", color=0x00FF00)
                    embed.set_thumbnail(url=next_track.artwork or bot.user.display_avatar.url)
                    embed.add_field(name="Song", value=f"{next_track.title}", inline=False)
                    await channel.send(content=f"Now Playing: {next_track.title}", embed=embed, view=MusicView())
        except: pass
    else:
        if not twentyfour_seven.get(guild_id, False):
            try:
                await asyncio.sleep(3)
                if player.queue.is_empty:
                    await player.disconnect()
            except: pass

@bot.event
async def on_member_join(member):
    if automod_config[member.guild.id]["fban"]:
        if any(w in member.name.lower() for w in NICK_BAN_WORDS) or any(w in str(member).lower() for w in BAD_WORDS):
            try:
                await member.ban(reason="F-Ban")
                return
            except: pass
    if welcome_enabled[member.guild.id] and welcome_config[member.guild.id]["enabled"]:
        cfg = welcome_config[member.guild.id]
        ch_id = cfg.get("channel") or welcome_channels.get(member.guild.id)
        if ch_id:
            ch = member.guild.get_channel(ch_id)
            if ch:
                try:
                    msg = cfg["message"].format(user=member.mention, server=member.guild.name, count=member.guild.member_count, username=str(member))
                    if cfg["embed_enabled"]:
                        title = cfg["embed_title"].format(user=str(member), server=member.guild.name, count=member.guild.member_count)
                        desc = cfg["embed_description"].format(user=member.mention, server=member.guild.name, count=member.guild.member_count, username=str(member))
                        embed = discord.Embed(title=title, description=desc, color=cfg["embed_color"])
                        if cfg["embed_thumbnail"]:
                            embed.set_thumbnail(url=member.display_avatar.url)
                        if cfg["embed_image"]:
                            embed.set_image(url=cfg["embed_image"])
                        embed.set_footer(text=f"Greet to {member.guild.name}")
                        await ch.send(content=msg, embed=embed)
                    else:
                        await ch.send(msg)
                except Exception as e:
                    print(f"Greet error: {e}")

# ===================== ANTINUKE EVENTS =====================
@bot.event
async def on_guild_channel_delete(channel):
    guild = channel.guild
    cfg = antinuke_config[guild.id]
    if not cfg["enabled"] or not cfg["protect_channels"]:
        return
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if entry.target.id == channel.id:
                executor = entry.user
                if executor.id == bot.user.id: return
                if executor.id == guild.owner_id: return
                if executor.id in cfg["whitelist"]: return
                if executor.id == OWNER_ID: return
                if guild.get_member(executor.id) and guild.get_member(executor.id).guild_permissions.administrator:
                    # Check if admin is whitelisted, if not punish still if strict
                    pass
                # Punish
                punishment = cfg["punishment"]
                reason = f"AntiNuke: Deleted channel {channel.name}"
                try:
                    if punishment == "ban":
                        await guild.ban(executor, reason=reason)
                    elif punishment == "kick":
                        await guild.kick(executor, reason=reason)
                    elif punishment == "mute":
                        member = guild.get_member(executor.id)
                        if member:
                            until = discord.utils.utcnow() + timedelta(hours=1)
                            await member.timeout(until, reason=reason)
                except: pass
                # Log
                if cfg["log_channel"]:
                    log_ch = guild.get_channel(cfg["log_channel"])
                    if log_ch:
                        embed = discord.Embed(title="🛡️ AntiNuke Triggered", description=f"**User:** {executor} ({executor.id})\n**Action:** Deleted channel `{channel.name}`\n**Punishment:** {punishment}", color=0xFF0000)
                        await log_ch.send(embed=embed)
                break
    except: pass

@bot.event
async def on_guild_role_delete(role):
    guild = role.guild
    cfg = antinuke_config[guild.id]
    if not cfg["enabled"] or not cfg["protect_roles"]:
        return
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            if entry.target.id == role.id:
                executor = entry.user
                if executor.id == bot.user.id: return
                if executor.id == guild.owner_id: return
                if executor.id in cfg["whitelist"]: return
                punishment = cfg["punishment"]
                reason = f"AntiNuke: Deleted role {role.name}"
                try:
                    if punishment == "ban":
                        await guild.ban(executor, reason=reason)
                    elif punishment == "kick":
                        await guild.kick(executor, reason=reason)
                except: pass
                break
    except: pass

@bot.event
async def on_member_ban(guild, user):
    cfg = antinuke_config[guild.id]
    if not cfg["enabled"] or not cfg["protect_bans"]:
        return
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                executor = entry.user
                if executor.id == bot.user.id: return
                if executor.id == guild.owner_id: return
                if executor.id in cfg["whitelist"]: return
                # Check mass ban
                recent_actions[guild.id].append(time.time())
                recent_actions[guild.id] = [t for t in recent_actions[guild.id] if time.time() - t < 10]
                if len(recent_actions[guild.id]) > 3:
                    punishment = cfg["punishment"]
                    reason = f"AntiNuke: Mass ban detected"
                    try:
                        if punishment == "ban":
                            await guild.ban(executor, reason=reason)
                        elif punishment == "kick":
                            await guild.kick(executor, reason=reason)
                    except: pass
                break
    except: pass

@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.guild and not is_staff(message.author):
        cfg = automod_config[message.guild.id]
        content = message.content.lower()
        # AntiSpam check
        if cfg["antispam"] or cfg["spam"]:
            tracker = spam_tracker[message.author.id]
            tracker.append(time.time())
            # 5 messages in 3 seconds
            if len(tracker) >= 5:
                if tracker[-1] - tracker[-5] < 3:
                    try:
                        await message.channel.purge(limit=5, check=lambda m: m.author.id == message.author.id)
                        await apply_punishment(message.author, message.guild, "antispam", "Spamming")
                        await message.channel.send(f"{message.author.mention} AntiSpam: Please slow down! Punishment: {automod_punishment[message.guild.id]['antispam']}", delete_after=5)
                        spam_tracker[message.author.id].clear()
                        return
                    except: pass
        if (cfg["invite"] or cfg["antiinvite"] or cfg["antilink"]) and ("discord.gg" in content or "discord.com/invite" in content or "discordapp.com/invite" in content or "http://" in content or "https://" in content):
            if "discord.gg" in content or "discord.com/invite" in content:
                try:
                    await message.delete()
                    await apply_punishment(message.author, message.guild, "antiinvite", "Invite link")
                    await message.channel.send(f"{message.author.mention} AntiInvite: Invites are not allowed. Punishment: {automod_punishment[message.guild.id]['antiinvite']}", delete_after=5)
                    return
                except: pass
        if (cfg["badwords"] or cfg["antibadword"]) and any(w in content for w in BAD_WORDS):
            try:
                await message.delete()
                await apply_punishment(message.author, message.guild, "antibadword", "Bad words")
                await message.channel.send(f"{message.author.mention} AntiBadWord: Bad words are not allowed. Punishment: {automod_punishment[message.guild.id]['antibadword']}", delete_after=5)
                return
            except: pass
        if (cfg["everyone"] or cfg["antieveryone"]) and ("@everyone" in content or "@here" in content):
            if not message.author.guild_permissions.mention_everyone:
                try:
                    await message.delete()
                    await apply_punishment(message.author, message.guild, "antieveryone", "Everyone ping")
                    await message.channel.send(f"{message.author.mention} AntiEveryone: Don't ping everyone. Punishment: {automod_punishment[message.guild.id]['antieveryone']}", delete_after=5)
                    return
                except: pass
        if (cfg["caps"] or cfg["anticaps"]) and len(content) > 10 and sum(1 for c in content if c.isupper()) / len(content) > 0.7:
            try:
                await message.delete()
                await apply_punishment(message.author, message.guild, "anticaps", "Too many caps")
                await message.channel.send(f"{message.author.mention} AntiCaps: Too many caps. Punishment: {automod_punishment[message.guild.id]['anticaps']}", delete_after=5)
                return
            except: pass
        if cfg["fban"]:
            if any(w in message.author.name.lower() for w in NICK_BAN_WORDS):
                try: await message.author.ban(reason="F-Ban"); return
                except: pass
        if cfg["nickban"]:
            if message.author.display_name and any(w in message.author.display_name.lower() for w in NICK_BAN_WORDS):
                try: await message.author.edit(nick="Filtered Name", reason="Nick Ban")
                except: pass
        # AntiRaid - mass join detection
        if cfg["antiraid"]:
            recent_actions[f"join_{message.guild.id}"].append(time.time())
            recent_actions[f"join_{message.guild.id}"] = [t for t in recent_actions[f"join_{message.guild.id}"] if time.time() - t < 10]
            if len(recent_actions[f"join_{message.guild.id}"]) > 10:
                try:
                    await message.guild.default_role.edit(permissions=discord.Permissions.none())
                    await message.channel.send("🛡️ AntiRaid: Possible raid detected! Locked server.", delete_after=10)
                except: pass
    if message.guild and not message.author.bot:
        lower = message.content.lower().strip()
        for trigger, response in AUTORESPONDER.items():
            if trigger.lower() == lower or trigger.lower() in lower:
                try:
                    await message.channel.send(response)
                    break
                except: pass
    if bot.user.mentioned_in(message) and not message.mention_everyone and not message.author.bot:
        embed = discord.Embed(title="✦ Cloudie • Premium", description=f"Greet, {message.author.mention}!\n\n⚡ Premium Bot System\n🎵 Fast Music • 🛡️ AutoMod • 💣 AntiNuke • 🤖 AutoResponder\n📖 Use {PREFIX}help or /help to explore commands.", color=0xC9A7F5)
        embed.set_footer(text="Cloudie • Premium Bot 🎧 | APP + Supports Commands")
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        await message.channel.send(embed=embed, view=MentionView())
    await bot.process_commands(message)

# ===================== MODERATION COMMANDS =====================
@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban_cmd(ctx, member: discord.Member, *, reason="No reason"):
    if member.id == ctx.author.id: return await ctx.send("You cannot ban yourself.")
    if member.id == bot.user.id: return await ctx.send("I cannot ban myself.")
    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
        return await ctx.send("You cannot ban someone with higher role.")
    try:
        dm_success, dm_embed = await dm_user(member, "Banned", ctx.guild, reason, None, ctx.author)
        if not dm_success:
            try:
                await ctx.send(f"{member.mention} Your DMs are closed. Here is your ban information!", embed=dm_embed)
                await asyncio.sleep(1)
            except: pass
        await asyncio.sleep(0.5)
        await member.ban(reason=f"{reason} | By {ctx.author}")
        embed = discord.Embed(title="Member Banned", color=0xFF0000)
        embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="DM", value="Sent" if dm_success else "Failed - DMs closed", inline=True)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick_cmd(ctx, member: discord.Member, *, reason="No reason"):
    if member.id == ctx.author.id: return await ctx.send("You cannot kick yourself.")
    try:
        dm_success, dm_embed = await dm_user(member, "Kicked", ctx.guild, reason, None, ctx.author)
        if not dm_success:
            try:
                await ctx.send(f"{member.mention} Your DMs are closed!", embed=dm_embed)
                await asyncio.sleep(1)
            except: pass
        await asyncio.sleep(0.3)
        await member.kick(reason=f"{reason} | By {ctx.author}")
        embed = discord.Embed(title="Member Kicked", color=0xFF6B00)
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.add_field(name="DM", value="Sent" if dm_success else "Failed", inline=True)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command(name="mute", aliases=["timeout"])
@commands.has_permissions(moderate_members=True)
async def mute_cmd(ctx, member: discord.Member, duration: int = 10, *, reason="No reason"):
    if member.id == ctx.author.id: return await ctx.send("You cannot mute yourself.")
    try:
        until = discord.utils.utcnow() + timedelta(minutes=duration)
        dm_success, dm_embed = await dm_user(member, "Muted", ctx.guild, reason, f"{duration} minutes", ctx.author)
        if not dm_success:
            try:
                await ctx.send(f"{member.mention} Your DMs are closed!", embed=dm_embed)
            except: pass
        await member.timeout(until, reason=reason)
        embed = discord.Embed(title="Member Muted", color=0xFFA500)
        embed.add_field(name="User", value=f"{member.mention}", inline=False)
        embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.add_field(name="DM", value="Sent" if dm_success else "Failed", inline=True)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command(name="unmute")
@commands.has_permissions(moderate_members=True)
async def unmute_cmd(ctx, member: discord.Member, *, reason="No reason"):
    try:
        await member.timeout(None, reason=reason)
        embed = discord.Embed(title="Member Unmuted", description=f"{member.mention} unmuted.", color=0x00FF00)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command(name="warn")
@commands.has_permissions(manage_messages=True)
async def warn_cmd(ctx, member: discord.Member, *, reason="No reason"):
    if member.id == bot.user.id:
        return await ctx.send("Can't warn bot.")
    warnings[member.id].append({"reason": reason, "mod": ctx.author.id, "time": time.time()})
    dm_success, dm_embed = await dm_user(member, "Warned", ctx.guild, reason, None, ctx.author)
    if not dm_success:
        try:
            await ctx.send(f"{member.mention} Your DMs are closed!", embed=dm_embed)
        except: pass
    embed = discord.Embed(title="Member Warned", color=0xFFFF00)
    embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Reason", value=f"{reason}", inline=False)
    embed.add_field(name="Total Warns", value=f"{len(warnings[member.id])}", inline=True)
    embed.add_field(name="DM", value="Sent" if dm_success else "Failed", inline=True)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@bot.command(name="warnings", aliases=["warns"])
async def warnings_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_warns = warnings.get(member.id, [])
    if not user_warns:
        return await ctx.send(f"{member.mention} has no warnings.")
    desc = ""
    for i, w in enumerate(user_warns[-10:], 1):
        desc += f"{i}. {w['reason'][:50]} - <@{w['mod']}> - <t:{int(w['time'])}:R>\n"
    embed = discord.Embed(title=f"Warnings - {member}", description=desc, color=0xFFFF00)
    await ctx.send(embed=embed)

@bot.command(name="clear", aliases=["purge"])
@commands.has_permissions(manage_messages=True)
async def clear_cmd(ctx, amount: int = 5):
    if amount < 1 or amount > 100: return await ctx.send("Amount 1-100.")
    try:
        deleted = await ctx.channel.purge(limit=amount+1)
        await ctx.send(f"Deleted {len(deleted)-1} messages.", delete_after=3)
    except Exception as e:
        await ctx.send(f"Failed: {e}")

@bot.command(name="lock")
@commands.has_permissions(manage_channels=True)
async def lock_cmd(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    try:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"{channel.mention} locked.")
    except Exception as e:
        await ctx.send(f"{e}")

@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def unlock_cmd(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    try:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(f"{channel.mention} unlocked.")
    except Exception as e:
        await ctx.send(f"{e}")

@bot.command(name="hide")
@commands.has_permissions(manage_channels=True)
async def hide_cmd(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    try:
        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await ctx.send(f"{channel.mention} hidden.")
    except Exception as e:
        await ctx.send(f"{e}")

@bot.command(name="unhide")
@commands.has_permissions(manage_channels=True)
async def unhide_cmd(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    try:
        await channel.set_permissions(ctx.guild.default_role, view_channel=True)
        await ctx.send(f"{channel.mention} unhidden.")
    except Exception as e:
        await ctx.send(f"{e}")

@bot.command(name="slowmode")
@commands.has_permissions(manage_channels=True)
async def slowmode_cmd(ctx, seconds: int = 0):
    try:
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Slowmode {seconds}s.")
    except Exception as e:
        await ctx.send(f"{e}")

@bot.command(name="nuke")
@commands.has_permissions(manage_channels=True)
async def nuke_cmd(ctx):
    try:
        channel = ctx.channel
        new_channel = await channel.clone(reason=f"Nuked by {ctx.author}")
        await channel.delete(reason=f"Nuked by {ctx.author}")
        embed = discord.Embed(title="Channel Nuked", description=f"Nuked by {ctx.author.mention}", color=0xFF0000)
        await new_channel.send(embed=embed)
    except Exception as e:
        await ctx.send(f"{e}")

@bot.command(name="nick")
@commands.has_permissions(manage_nicknames=True)
async def nick_cmd(ctx, member: discord.Member, *, nickname=None):
    try:
        if nickname is None:
            await member.edit(nick=None, reason=f"Reset by {ctx.author}")
            await ctx.send(f"Reset nick for {member.mention}")
        else:
            if any(w in nickname.lower() for w in NICK_BAN_WORDS):
                return await ctx.send(f"Nick contains banned word.")
            await member.edit(nick=nickname, reason=f"By {ctx.author}")
            await ctx.send(f"Changed nick for {member.mention} to {nickname}")
    except Exception as e:
        await ctx.send(f"{e}")

@bot.command(name="addbadword")
@commands.has_permissions(administrator=True)
async def addbadword_cmd(ctx, *, word: str):
    word = word.lower().strip()
    if word in BAD_WORDS: return await ctx.send(f"Already exists.")
    BAD_WORDS.append(word)
    save_badwords()
    await ctx.send(f"Added badword: {word}")

@bot.command(name="removebadword")
@commands.has_permissions(administrator=True)
async def removebadword_cmd(ctx, *, word: str):
    word = word.lower().strip()
    if word not in BAD_WORDS: return await ctx.send(f"Not found.")
    BAD_WORDS.remove(word)
    save_badwords()
    await ctx.send(f"Removed badword: {word}")

@bot.command(name="badwordlist")
@commands.has_permissions(administrator=True)
async def badwordlist_cmd(ctx):
    if not BAD_WORDS: return await ctx.send("No badwords.")
    desc = "\n".join([f"{i}. {w}" for i, w in enumerate(BAD_WORDS, 1)])
    embed = discord.Embed(title="Badword List", description=desc[:4000], color=0xFF0000)
    await ctx.send(embed=embed)

@bot.command(name="fban")
@commands.has_permissions(administrator=True)
async def fban_cmd(ctx, mode: str = None):
    if mode is None:
        status = "ON" if automod_config[ctx.guild.id]["fban"] else "OFF"
        return await ctx.send(f"F-Ban: {status} Use {PREFIX}fban on/off")
    if mode.lower() in ["on", "enable"]:
        automod_config[ctx.guild.id]["fban"] = True
        save_automod_config()
        await ctx.send("F-Ban enabled.")
    elif mode.lower() in ["off", "disable"]:
        automod_config[ctx.guild.id]["fban"] = False
        save_automod_config()
        await ctx.send("F-Ban disabled.")

@bot.command(name="nickban")
@commands.has_permissions(administrator=True)
async def nickban_cmd(ctx, action: str = None, *, word: str = None):
    if action is None:
        status = "ON" if automod_config[ctx.guild.id]["nickban"] else "OFF"
        list_words = ", ".join(NICK_BAN_WORDS) if NICK_BAN_WORDS else "None"
        embed = discord.Embed(title="Nick-Ban", description=f"Status: {status}\nWords: {list_words}\n{PREFIX}nickban on/off/add <word>/remove <word>/list", color=0xC9A7F5)
        return await ctx.send(embed=embed)
    action = action.lower()
    if action in ["on", "enable"]:
        automod_config[ctx.guild.id]["nickban"] = True
        save_automod_config()
        await ctx.send("Nick-Ban enabled.")
    elif action in ["off", "disable"]:
        automod_config[ctx.guild.id]["nickban"] = False
        save_automod_config()
        await ctx.send("Nick-Ban disabled.")
    elif action == "add" and word:
        word = word.lower().strip()
        if word not in NICK_BAN_WORDS:
            NICK_BAN_WORDS.append(word)
            save_nickban()
            await ctx.send(f"Added to nick-ban: {word}")
        else:
            await ctx.send("Already exists.")
    elif action == "remove" and word:
        word = word.lower().strip()
        if word in NICK_BAN_WORDS:
            NICK_BAN_WORDS.remove(word)
            save_nickban()
            await ctx.send(f"Removed from nick-ban: {word}")
        else:
            await ctx.send("Not found.")
    elif action == "list":
        desc = ", ".join(NICK_BAN_WORDS) if NICK_BAN_WORDS else "None"
        await ctx.send(f"Nick-Ban words: {desc}")

# ===================== NEW AUTOMOD SYSTEM =====================
@bot.command(name="automod")
@commands.has_permissions(administrator=True)
async def automod_cmd(ctx, feature: str = None, mode: str = None):
    cfg = automod_config[ctx.guild.id]
    pun = automod_punishment[ctx.guild.id]
    if feature is None:
        desc = "**Current AutoMod Configuration:**\n\n"
        for k,v in cfg.items():
            if k in ["fban", "nickban"]: continue
            desc += f"**{k}:** {'🟢 ON' if v else '🔴 OFF'} | Punishment: `{pun.get(k, 'delete')}`\n"
        desc += f"\n**Commands:**\n{PREFIX}automod <feature> on/off\n{PREFIX}automod punishment <feature> <delete/warn/mute/kick/ban>\n{PREFIX}automod panel - Open control panel\n{PREFIX}antinuke on/off - Toggle AntiNuke"
        embed = discord.Embed(title="🛡️ AutoMod Control Panel", description=desc, color=0xC9A7F5)
        embed.add_field(name="Available Features", value="antinuke, antispam, anticaps, antibadword, antilink, antieveryone, antiinvite, antiraid", inline=False)
        embed.add_field(name="Punishments", value="delete, warn, mute (10m), kick, ban, rename, timeout", inline=False)
        view = AutomodView(ctx.guild.id)
        return await ctx.send(embed=embed, view=view)
    feature = feature.lower()
    if feature == "panel":
        desc = ""
        for k,v in cfg.items():
            if k in ["fban", "nickban"]: continue
            desc += f"**{k}:** {'🟢 ON' if v else '🔴 OFF'} | Punish: `{pun.get(k, 'delete')}`\n"
        embed = discord.Embed(title="🛡️ AutoMod Panel - Full Control", description=desc, color=0xC9A7F5)
        view = AutomodView(ctx.guild.id)
        return await ctx.send(embed=embed, view=view)
    if feature == "punishment" and mode:
        parts = mode.split()
        if len(parts) < 2:
            return await ctx.send(f"Usage: {PREFIX}automod punishment <feature> <delete/warn/mute/kick/ban>")
        feat = parts[0].lower()
        punish = parts[1].lower()
        if feat not in pun:
            return await ctx.send(f"Invalid feature. Available: {', '.join(pun.keys())}")
        if punish not in ["delete", "warn", "mute", "kick", "ban", "rename", "timeout"]:
            return await ctx.send(f"Invalid punishment. Use: delete, warn, mute, kick, ban, rename, timeout")
        pun[feat] = punish
        save_automod_punishment()
        return await ctx.send(f"Punishment for **{feat}** set to **{punish}** ✅")
    if feature not in cfg: return await ctx.send(f"Invalid feature. Available: {', '.join(cfg.keys())}")
    if mode is None:
        status = "ON" if cfg[feature] else "OFF"
        return await ctx.send(f"{feature}: {status} | Punishment: {pun.get(feature, 'delete')} | Use {PREFIX}automod {feature} on/off")
    if mode.lower() in ["on", "enable"]:
        cfg[feature] = True
        save_automod_config()
        await ctx.send(f"✅ {feature} enabled. Punishment: {pun.get(feature, 'delete')}")
    elif mode.lower() in ["off", "disable"]:
        cfg[feature] = False
        save_automod_config()
        await ctx.send(f"❌ {feature} disabled.")

@bot.command(name="antinuke")
@commands.has_permissions(administrator=True)
async def antinuke_cmd(ctx, action: str = None, *, extra: str = None):
    cfg = antinuke_config[ctx.guild.id]
    if action is None:
        embed = discord.Embed(title="💣 AntiNuke System", description=f"**Status:** {'🟢 ON' if cfg['enabled'] else '🔴 OFF'}\n**Punishment:** `{cfg['punishment']}`\n**Whitelist:** {len(cfg['whitelist'])} users\n**Protect Channels:** {'ON' if cfg['protect_channels'] else 'OFF'}\n**Protect Roles:** {'ON' if cfg['protect_roles'] else 'OFF'}\n**Protect Bans:** {'ON' if cfg['protect_bans'] else 'OFF'}\n\n**Commands:**\n{PREFIX}antinuke on/off\n{PREFIX}antinuke punishment <ban/kick/mute>\n{PREFIX}antinuke whitelist add/remove <@user>\n{PREFIX}antinuke log #channel\n{PREFIX}antinuke panel", color=0xFF0000)
        return await ctx.send(embed=embed)
    action = action.lower()
    if action in ["on", "enable"]:
        cfg["enabled"] = True
        automod_config[ctx.guild.id]["antinuke"] = True
        save_antinuke_config()
        save_automod_config()
        await ctx.send("💣 AntiNuke **ENABLED** - Server is now protected! 🛡️")
    elif action in ["off", "disable"]:
        cfg["enabled"] = False
        automod_config[ctx.guild.id]["antinuke"] = False
        save_antinuke_config()
        save_automod_config()
        await ctx.send("💣 AntiNuke **DISABLED**")
    elif action == "punishment" and extra:
        if extra.lower() in ["ban", "kick", "mute"]:
            cfg["punishment"] = extra.lower()
            save_antinuke_config()
            await ctx.send(f"AntiNuke punishment set to **{extra.lower()}**")
        else:
            await ctx.send("Punishment must be ban, kick, or mute")
    elif action == "whitelist":
        if not extra:
            wl = cfg["whitelist"]
            if not wl:
                return await ctx.send("Whitelist is empty. No one is whitelisted.")
            desc = "\n".join([f"<@{uid}> ({uid})" for uid in wl[:20]])
            embed = discord.Embed(title="AntiNuke Whitelist", description=desc, color=0x00FF00)
            return await ctx.send(embed=embed)
        parts = extra.split()
        if len(parts) < 2:
            return await ctx.send(f"Usage: {PREFIX}antinuke whitelist add/remove <@user>")
        sub = parts[0].lower()
        try:
            user_id = int(re.sub(r'\D', '', parts[1]))
        except:
            return await ctx.send("Invalid user. Mention a user.")
        if sub == "add":
            if user_id not in cfg["whitelist"]:
                cfg["whitelist"].append(user_id)
                save_antinuke_config()
                await ctx.send(f"Added <@{user_id}> to AntiNuke whitelist ✅")
            else:
                await ctx.send("User already whitelisted.")
        elif sub == "remove":
            if user_id in cfg["whitelist"]:
                cfg["whitelist"].remove(user_id)
                save_antinuke_config()
                await ctx.send(f"Removed <@{user_id}> from whitelist")
            else:
                await ctx.send("User not in whitelist.")
    elif action == "log" and extra:
        try:
            ch_id = int(re.sub(r'\D', '', extra))
            ch = ctx.guild.get_channel(ch_id)
            if ch:
                cfg["log_channel"] = ch_id
                save_antinuke_config()
                await ctx.send(f"AntiNuke log channel set to {ch.mention}")
            else:
                await ctx.send("Channel not found.")
        except:
            await ctx.send(f"Usage: {PREFIX}antinuke log #channel")
    elif action == "panel":
        embed = discord.Embed(title="💣 AntiNuke Control Panel", description=f"**Status:** {'🟢 ON' if cfg['enabled'] else '🔴 OFF'}\n**Punishment:** {cfg['punishment']}\n**Whitelist:** {len(cfg['whitelist'])} users", color=0xFF0000)
        view = AutomodView(ctx.guild.id)
        await ctx.send(embed=embed, view=view)

@bot.group(name="autoresponder", aliases=["ar", "autores"], invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def autoresponder_group(ctx):
    if not AUTORESPONDER:
        return await ctx.send(f"No autoresponders. Use {PREFIX}ar add <trigger> <response>")
    desc = ""
    for i, (trig, resp) in enumerate(AUTORESPONDER.items(), 1):
        desc += f"{i}. {trig} -> {resp[:50]}\n"
    embed = discord.Embed(title="AutoResponder List", description=desc[:4000], color=0xC9A7F5)
    await ctx.send(embed=embed)

@autoresponder_group.command(name="add")
@commands.has_permissions(administrator=True)
async def ar_add(ctx, trigger: str, *, response: str):
    trigger = trigger.lower().strip()
    AUTORESPONDER[trigger] = response
    save_autoresponder()
    embed = discord.Embed(title="AutoResponder Added", color=0x00FF00)
    embed.add_field(name="Trigger", value=f"{trigger}", inline=False)
    embed.add_field(name="Response", value=response[:1000], inline=False)
    await ctx.send(embed=embed)

@autoresponder_group.command(name="remove", aliases=["delete", "del"])
@commands.has_permissions(administrator=True)
async def ar_remove(ctx, *, trigger: str):
    trigger = trigger.lower().strip()
    if trigger not in AUTORESPONDER:
        return await ctx.send(f"Trigger not found: {trigger}")
    del AUTORESPONDER[trigger]
    save_autoresponder()
    await ctx.send(f"Removed autoresponder: {trigger}")

@autoresponder_group.command(name="list")
async def ar_list(ctx):
    if not AUTORESPONDER:
        return await ctx.send("No autoresponders.")
    desc = ""
    for i, (trig, resp) in enumerate(AUTORESPONDER.items(), 1):
        desc += f"{i}. {trig} -> {resp[:80]}\n"
    embed = discord.Embed(title="AutoResponder List", description=desc[:4000], color=0xC9A7F5)
    await ctx.send(embed=embed)

@autoresponder_group.command(name="clear")
@commands.has_permissions(administrator=True)
async def ar_clear(ctx):
    AUTORESPONDER.clear()
    save_autoresponder()
    await ctx.send("Cleared all autoresponders.")

# ===================== WELCOME SYSTEM - PREMIUM MENU =====================
class WelcomeMessageModal(discord.ui.Modal, title="Set Greet Message"):
    message = discord.ui.TextInput(label="Greet Message", style=discord.TextStyle.paragraph, placeholder="Greet {user} to {server}! You are member #{count}", required=True, max_length=1000)
    async def on_submit(self, interaction: discord.Interaction):
        cfg = welcome_config[interaction.guild.id]
        cfg["message"] = self.message.value
        save_welcome_config()
        await interaction.response.send_message(f"✅ Greet message set to:\n{self.message.value[:500]}", ephemeral=True)

class WelcomeTitleModal(discord.ui.Modal, title="Set Embed Title"):
    title_input = discord.ui.TextInput(label="Embed Title", placeholder="Greet to {server}!", required=True, max_length=256)
    async def on_submit(self, interaction: discord.Interaction):
        cfg = welcome_config[interaction.guild.id]
        cfg["embed_title"] = self.title_input.value
        save_welcome_config()
        await interaction.response.send_message(f"✅ Embed title set to: {self.title_input.value}", ephemeral=True)

class WelcomeDescModal(discord.ui.Modal, title="Set Embed Description"):
    desc = discord.ui.TextInput(label="Embed Description", style=discord.TextStyle.paragraph, placeholder="Hey {user}, welcome to {server}!", required=True, max_length=2000)
    async def on_submit(self, interaction: discord.Interaction):
        cfg = welcome_config[interaction.guild.id]
        cfg["embed_description"] = self.desc.value
        save_welcome_config()
        await interaction.response.send_message(f"✅ Embed description set!", ephemeral=True)

class WelcomeImageModal(discord.ui.Modal, title="Set Greet Image (Link)"):
    image_url = discord.ui.TextInput(label="Image URL (embed image)", placeholder="https://example.com/image.png or none", required=False, max_length=500)
    thumb_url = discord.ui.TextInput(label="Thumbnail URL (optional)", placeholder="https://example.com/thumb.png or leave empty", required=False, max_length=500)
    async def on_submit(self, interaction: discord.Interaction):
        cfg = welcome_config[interaction.guild.id]
        if self.image_url.value.lower() in ["none", "remove", "delete", ""]:
            cfg["embed_image"] = None
        else:
            cfg["embed_image"] = self.image_url.value.strip()
        # Thumbnail handling - if provided use as custom thumbnail flag
        if self.thumb_url.value.strip():
            cfg["custom_thumb_url"] = self.thumb_url.value.strip()
            cfg["embed_thumbnail"] = True
        save_welcome_config()
        await interaction.response.send_message(f"✅ Image set!\nImage: {cfg['embed_image'] or 'None'}\nThumb: {self.thumb_url.value or 'Member avatar'}", ephemeral=True)

class WelcomeColorModal(discord.ui.Modal, title="Set Embed Color"):
    color = discord.ui.TextInput(label="Hex Color", placeholder="#00FF00 or 00FF00", required=True, max_length=20)
    async def on_submit(self, interaction: discord.Interaction):
        cfg = welcome_config[interaction.guild.id]
        try:
            col = self.color.value.replace("#", "").strip()
            cfg["embed_color"] = int(col, 16)
            save_welcome_config()
            await interaction.response.send_message(f"✅ Color set to #{col}", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Invalid color. Use #00FF00 format", ephemeral=True)

class WelcomeSetupView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=300)
        self.guild_id = guild_id

    def get_embed(self):
        cfg = welcome_config[self.guild_id]
        ch = cfg.get("channel") or welcome_channels.get(self.guild_id)
        ch_mention = f"<#{ch}>" if ch else "❌ Not set"
        embed = discord.Embed(title="👋 Greet System - PREMIUM MENU", description=f"**Status:** {'🟢 ON' if cfg['enabled'] else '🔴 OFF'}\n**Channel:** {ch_mention}\n**Embed:** {'🟢 ON' if cfg['embed_enabled'] else '🔴 OFF'} | **Thumbnail:** {'ON' if cfg['embed_thumbnail'] else 'OFF'}\n\n**Current Config:**\n**Message:** {cfg['message'][:100]}...\n**Title:** {cfg['embed_title']}\n**Desc:** {cfg['embed_description'][:100]}...\n**Color:** #{hex(cfg['embed_color'])[2:]}\n**Image:** {'Set ✅' if cfg['embed_image'] else 'Not set ❌'}\n\n**Placeholders:** `{{user}}` `{{server}}` `{{count}}` `{{username}}`\n\nUse buttons below to setup!", color=0xE7D6FF)
        embed.set_footer(text="Cloudie • Premium Greet • Fully Customizable")
        if cfg['embed_image']:
            embed.set_image(url=cfg['embed_image'])
        return embed

    @discord.ui.button(label="Set Channel", emoji="📢", style=discord.ButtonStyle.blurple, row=0)
    async def set_channel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Use {PREFIX}setgreet #channel to set channel", ephemeral=True)

    @discord.ui.button(label="Set Message", emoji="💬", style=discord.ButtonStyle.gray, row=0)
    async def set_msg_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WelcomeMessageModal())

    @discord.ui.button(label="Set Title", emoji="📝", style=discord.ButtonStyle.gray, row=0)
    async def set_title_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WelcomeTitleModal())

    @discord.ui.button(label="Set Description", emoji="📄", style=discord.ButtonStyle.gray, row=0)
    async def set_desc_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WelcomeDescModal())

    @discord.ui.button(label="Set Image Link", emoji="🖼️", style=discord.ButtonStyle.green, row=1)
    async def set_image_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WelcomeImageModal())

    @discord.ui.button(label="Set Color", emoji="🎨", style=discord.ButtonStyle.green, row=1)
    async def set_color_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WelcomeColorModal())

    @discord.ui.button(label="Toggle Embed", emoji="✨", style=discord.ButtonStyle.blurple, row=1)
    async def toggle_embed_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cfg = welcome_config[self.guild_id]
        cfg["embed_enabled"] = not cfg["embed_enabled"]
        save_welcome_config()
        await interaction.response.send_message(f"Embed: {'ON' if cfg['embed_enabled'] else 'OFF'}", ephemeral=True)

    @discord.ui.button(label="Toggle ON/OFF", emoji="🔴", style=discord.ButtonStyle.red, row=1)
    async def toggle_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cfg = welcome_config[self.guild_id]
        cfg["enabled"] = not cfg["enabled"]
        welcome_enabled[self.guild_id] = cfg["enabled"]
        save_welcome_config()
        await interaction.response.send_message(f"Greet: {'ON' if cfg['enabled'] else 'OFF'}", ephemeral=True)

    @discord.ui.button(label="Test Greet", emoji="🧪", style=discord.ButtonStyle.green, row=2)
    async def test_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cfg = welcome_config[self.guild_id]
        ch_id = cfg.get("channel") or welcome_channels.get(self.guild_id)
        if not ch_id:
            return await interaction.response.send_message("❌ Channel not set. Use /setwelcome #channel first", ephemeral=True)
        ch = interaction.guild.get_channel(ch_id)
        if not ch:
            return await interaction.response.send_message("❌ Channel not found", ephemeral=True)
        try:
            msg = cfg["message"].format(user=interaction.user.mention, server=interaction.guild.name, count=interaction.guild.member_count, username=str(interaction.user))
            if cfg["embed_enabled"]:
                title = cfg["embed_title"].format(user=str(interaction.user), server=interaction.guild.name, count=interaction.guild.member_count)
                desc = cfg["embed_description"].format(user=interaction.user.mention, server=interaction.guild.name, count=interaction.guild.member_count, username=str(interaction.user))
                embed = discord.Embed(title=title, description=desc, color=cfg["embed_color"])
                if cfg["embed_thumbnail"]:
                    thumb_url = cfg.get("custom_thumb_url")
                    if thumb_url:
                        embed.set_thumbnail(url=thumb_url)
                    else:
                        embed.set_thumbnail(url=interaction.user.display_avatar.url)
                if cfg["embed_image"]:
                    embed.set_image(url=cfg["embed_image"])
                embed.set_footer(text=f"Greet to {interaction.guild.name} • Premium")
                await ch.send(content=msg, embed=embed)
            else:
                await ch.send(msg)
            await interaction.response.send_message(f"✅ Test sent to {ch.mention}!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed: {e}", ephemeral=True)

    @discord.ui.button(label="Preview", emoji="👁️", style=discord.ButtonStyle.gray, row=2)
    async def preview_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cfg = welcome_config[self.guild_id]
        try:
            title = cfg["embed_title"].format(user=str(interaction.user), server=interaction.guild.name, count=interaction.guild.member_count)
            desc = cfg["embed_description"].format(user=interaction.user.mention, server=interaction.guild.name, count=interaction.guild.member_count, username=str(interaction.user))
            embed = discord.Embed(title=title, description=desc, color=cfg["embed_color"])
            if cfg["embed_thumbnail"]:
                thumb_url = cfg.get("custom_thumb_url")
                embed.set_thumbnail(url=thumb_url or interaction.user.display_avatar.url)
            if cfg["embed_image"]:
                embed.set_image(url=cfg["embed_image"])
            embed.set_footer(text="Preview • Cloudie Premium Greet")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Preview error: {e}", ephemeral=True)

@bot.command(name="greet", aliases=["welcome"])
@commands.has_permissions(administrator=True)
async def welcome_cmd(ctx, mode: str = None):
    cfg = welcome_config[ctx.guild.id]
    if mode is None:
        view = WelcomeSetupView(ctx.guild.id)
        embed = view.get_embed()
        return await ctx.send(embed=embed, view=view)
    if mode.lower() in ["on", "enable"]:
        cfg["enabled"] = True
        welcome_enabled[ctx.guild.id] = True
        save_welcome_config()
        view = WelcomeSetupView(ctx.guild.id)
        await ctx.send(f"✅ Greet enabled!", embed=view.get_embed(), view=view)
    elif mode.lower() in ["off", "disable"]:
        cfg["enabled"] = False
        welcome_enabled[ctx.guild.id] = False
        save_welcome_config()
        await ctx.send("❌ Greet disabled.")
    elif mode.lower() == "test":
        ch_id = cfg.get("channel") or welcome_channels.get(ctx.guild.id)
        if not ch_id:
            return await ctx.send(f"Channel not set. Use {PREFIX}setgreet #channel")
        ch = ctx.guild.get_channel(ch_id)
        if not ch:
            return await ctx.send("Channel not found.")
        try:
            msg = cfg["message"].format(user=ctx.author.mention, server=ctx.guild.name, count=ctx.guild.member_count, username=str(ctx.author))
            if cfg["embed_enabled"]:
                title = cfg["embed_title"].format(user=str(ctx.author), server=ctx.guild.name, count=ctx.guild.member_count)
                desc = cfg["embed_description"].format(user=ctx.author.mention, server=ctx.guild.name, count=ctx.guild.member_count, username=str(ctx.author))
                embed = discord.Embed(title=title, description=desc, color=cfg["embed_color"])
                if cfg["embed_thumbnail"]:
                    thumb = cfg.get("custom_thumb_url")
                    embed.set_thumbnail(url=thumb or ctx.author.display_avatar.url)
                if cfg["embed_image"]:
                    embed.set_image(url=cfg["embed_image"])
                await ch.send(content=msg, embed=embed)
            else:
                await ch.send(msg)
            await ctx.send(f"✅ Test sent to {ch.mention}")
        except Exception as e:
            await ctx.send(f"Failed: {e}")
    else:
        view = WelcomeSetupView(ctx.guild.id)
        await ctx.send(embed=view.get_embed(), view=view)

@bot.command(name="setgreet", aliases=["setwelcome"])
@commands.has_permissions(administrator=True)
async def setwelcome_cmd(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    welcome_channels[ctx.guild.id] = channel.id
    welcome_config[ctx.guild.id]["channel"] = channel.id
    save_welcome_config()
    view = WelcomeSetupView(ctx.guild.id)
    await ctx.send(f"✅ Greet channel set to {channel.mention}", embed=view.get_embed(), view=view)

@bot.command(name="greetconfig", aliases=["welcomeconfig", "wc"])
@commands.has_permissions(administrator=True)
async def welcomeconfig_cmd(ctx, setting: str = None, *, value: str = None):
    cfg = welcome_config[ctx.guild.id]
    if setting is None:
        view = WelcomeSetupView(ctx.guild.id)
        return await ctx.send(embed=view.get_embed(), view=view)
    setting = setting.lower()
    if value is None:
        return await ctx.send(f"Usage: {PREFIX}greetconfig <message/title/description/color/thumbnail/image/embed> <value> OR use {PREFIX}greet for premium menu")
    if setting == "message":
        cfg["message"] = value
        save_welcome_config()
        await ctx.send(f"✅ Message set!")
    elif setting == "title":
        cfg["embed_title"] = value
        save_welcome_config()
        await ctx.send(f"✅ Title set!")
    elif setting == "description":
        cfg["embed_description"] = value
        save_welcome_config()
        await ctx.send(f"✅ Description set!")
    elif setting == "color":
        try:
            color = int(value.replace("#", ""), 16)
            cfg["embed_color"] = color
            save_welcome_config()
            await ctx.send(f"✅ Color set to {value}")
        except:
            await ctx.send("Invalid color. Use #00FF00")
    elif setting in ["thumbnail", "thumb"]:
        if value.lower() in ["on", "true", "yes"]:
            cfg["embed_thumbnail"] = True
        elif value.lower() in ["off", "false", "no"]:
            cfg["embed_thumbnail"] = False
        else:
            cfg["custom_thumb_url"] = value
            cfg["embed_thumbnail"] = True
        save_welcome_config()
        await ctx.send(f"✅ Thumbnail set!")
    elif setting == "image":
        cfg["embed_image"] = value if value.lower() not in ["none", "remove"] else None
        save_welcome_config()
        await ctx.send(f"✅ Image set from link!")
    elif setting == "embed":
        if value.lower() in ["on", "true", "yes"]:
            cfg["embed_enabled"] = True
        else:
            cfg["embed_enabled"] = False
        save_welcome_config()
        await ctx.send(f"✅ Embed {cfg['embed_enabled']}")

@bot.command(name="ticket")
@commands.has_permissions(manage_channels=True)
async def ticket_cmd(ctx, action: str = None, *, value: str = None):
    cfg = ticket_config[ctx.guild.id]
    if action is None:
        embed = discord.Embed(title=cfg["embed_title"], description=cfg["embed_description"], color=cfg["embed_color"])
        if ctx.guild.icon: embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.add_field(name="Commands", value=f"{PREFIX}ticket panel - Send panel\n{PREFIX}ticket title <title>\n{PREFIX}ticket description <desc>\n{PREFIX}ticket color <hex>\n{PREFIX}ticket button <label>", inline=False)
        return await ctx.send(embed=embed, view=TicketView())
    action = action.lower()
    if action == "panel":
        embed = discord.Embed(title=cfg["embed_title"], description=cfg["embed_description"], color=cfg["embed_color"])
        if ctx.guild.icon: embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.send(embed=embed, view=TicketView())
    elif action == "title" and value:
        cfg["embed_title"] = value
        save_ticket_config()
        await ctx.send(f"✅ Ticket title set to: {value}")
    elif action == "description" and value:
        cfg["embed_description"] = value
        save_ticket_config()
        await ctx.send(f"✅ Ticket description set.")
    elif action == "color" and value:
        try:
            color = int(value.replace("#", ""), 16)
            cfg["embed_color"] = color
            save_ticket_config()
            await ctx.send(f"✅ Ticket color set to {value}")
        except:
            await ctx.send("Invalid color. Use hex like #00FF00")
    elif action == "button" and value:
        cfg["button_label"] = value
        save_ticket_config()
        await ctx.send(f"✅ Ticket button label set to: {value}")

@bot.command(name="close")
async def close_cmd(ctx):
    if "ticket-" not in ctx.channel.name: return await ctx.send("This is not a ticket channel.")
    await ctx.send("Closing ticket in 5 seconds...")
    await asyncio.sleep(5)
    try: await ctx.channel.delete(reason=f"Closed by {ctx.author}")
    except: pass

@bot.command(name="add")
@commands.has_permissions(manage_channels=True)
async def add_cmd(ctx, member: discord.Member):
    if "ticket-" not in ctx.channel.name: return await ctx.send("Only in ticket channel.")
    try:
        await ctx.channel.set_permissions(member, view_channel=True, send_messages=True)
        await ctx.send(f"{member.mention} added to ticket.")
    except Exception as e:
        await ctx.send(f"{e}")

@bot.command(name="remove")
@commands.has_permissions(manage_channels=True)
async def remove_cmd(ctx, member: discord.Member):
    if "ticket-" not in ctx.channel.name: return await ctx.send("Only in ticket channel.")
    try:
        await ctx.channel.set_permissions(member, overwrite=None)
        await ctx.send(f"{member.mention} removed from ticket.")
    except Exception as e:
        await ctx.send(f"{e}")

# ===================== REAL PING - FAKE HATA DIYA =====================
@bot.command(name="ping", aliases=["pong"])
async def ping_cmd(ctx):
    ws_ping = round(bot.latency * 1000) if bot.latency else 0
    start = time.time()
    msg = await ctx.send("Pinging...")
    db_ping = round((time.time() - start) * 1000, 1)
    uptime_seconds = int(time.time() - START_TIME)
    hours = uptime_seconds // 3600
    mins = (uptime_seconds % 3600) // 60
    uptime_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
    cache_count = len(get_queue(ctx.guild.id))
    total_nodes = len(NODE_CONFIGS)
    try:
        connected_nodes = len(wavelink.Pool.nodes) if hasattr(wavelink.Pool, 'nodes') else 0
    except:
        connected_nodes = 0
    embed = discord.Embed(color=0x2ECC71)
    embed.description = f"""## 📊 Pong! - Real Ping
🛰️ WebSocket: {ws_ping}ms
💾 Database: {db_ping}ms
🎵 Lavalink: {connected_nodes}/{total_nodes} nodes
📦 Queue: {cache_count} songs
⏰ Uptime: {uptime_str}
━━━━━━━━━━━━━━━━━━━━━━
✦ Cloudie • Premium Bot 🎧 | Real Ping"""
    await msg.edit(content=None, embed=embed)

@bot.command(name="pingboost")
async def pingboost_alias(ctx):
    ws_ping = round(bot.latency * 1000) if bot.latency else 0
    embed = discord.Embed(color=0x2ECC71)
    embed.description = f"""## 📊 Real Ping
🛰️ WebSocket: {ws_ping}ms
💾 Database: Real
🎵 Lavalink: {len(NODE_CONFIGS)} configured public nodes
━━━━━━━━━━━━━━━━━━━━━━
✦ Cloudie • Premium Bot 🎧 | No fake"""
    await ctx.send(embed=embed)

@bot.command(name="network", aliases=["net", "wifi"])
async def network_cmd(ctx):
    embed = discord.Embed(title="Network Info - Best Lavalink Hosting", color=0x00FF00)
    embed.add_field(name="Bot Latency", value=f"{round(bot.latency*1000)}ms Real", inline=True)
    embed.add_field(name="Platform", value=f"{platform.system()}", inline=True)
    embed.add_field(name="Lavalink Nodes", value=f"{len(NODE_CONFIGS)} public v4 nodes configured from lavalink_nodes.json. Public availability is not guaranteed.", inline=False)
    embed.add_field(name="Search Speed", value="⚡ 1-2 sec - Fixed 10s delay", inline=True)
    embed.add_field(name="Audio Quality", value="192k - No cracking - Fixed", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="avatar", aliases=["av"])
async def avatar_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member}'s Avatar", color=0xC9A7F5)
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="serverinfo", aliases=["si"])
async def serverinfo_cmd(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"{guild.name}", color=0xC9A7F5)
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Owner", value=f"{guild.owner_id}", inline=False)
    embed.add_field(name="Created", value=f"<t:{int(guild.created_at.timestamp())}:D>", inline=True)
    embed.add_field(name="Members", value=f"Total: {guild.member_count}", inline=True)
    embed.add_field(name="Security", value=f"AntiNuke: {'ON' if antinuke_config[guild.id]['enabled'] else 'OFF'}\nAutoMod: {sum(1 for v in automod_config[guild.id].values() if v)} features ON", inline=False)
    embed.set_footer(text=f"ID: {guild.id} | Prefix: {PREFIX} | Slash: /")
    await ctx.send(embed=embed)

@bot.command(name="userinfo", aliases=["ui", "whois"])
async def userinfo_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member}", color=0xC9A7F5)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=f"{member.id}", inline=True)
    embed.add_field(name="Created", value=f"<t:{int(member.created_at.timestamp())}:D>", inline=False)
    embed.add_field(name="Joined", value=f"<t:{int(member.joined_at.timestamp())}:D>" if member.joined_at else "Unknown", inline=False)
    await ctx.send(embed=embed)

# ===================== FIXED JOIN COMMAND =====================
@bot.command(name="join", aliases=["j", "connect"])
async def join_cmd(ctx):
    if not ctx.author.voice:
        return await ctx.send("You are not in a voice channel.")
    channel = ctx.author.voice.channel
    vc = ctx.voice_client
    if vc:
        try:
            await vc.move_to(channel)
            return await ctx.send(f"Moved to {channel.mention}")
        except Exception as e:
            return await ctx.send(f"Move failed: {e}")
    else:
        try:
            new_vc = await channel.connect(self_deaf=True)
            if hasattr(new_vc, "set_volume"):
                try:
                    await new_vc.set_volume(100)
                except:
                    pass
            await ctx.send(f"Joined {channel.mention}")
        except Exception as e:
            await ctx.send(f"Failed to join: {e}")

@bot.command(name="leave", aliases=["disconnect", "dc"])
async def leave_cmd(ctx):
    player = ctx.voice_client
    if not player:
        return await ctx.send("Not in VC.")
    twentyfour_seven[ctx.guild.id] = False
    save_247()
    await player.disconnect()
    await ctx.send("Left VC.")

@bot.command(name="play", aliases=["p"])
async def play_cmd(ctx, *, query: str):
    if not ctx.author.voice:
        return await ctx.send("Join a VC first! Use /join")
    if not ctx.voice_client:
        try:
            await ctx.author.voice.channel.connect(self_deaf=True)
        except Exception as e:
            return await ctx.send(f"VC join error: {e}")

    last_text_channel[ctx.guild.id] = ctx.channel.id
    last_requester[ctx.guild.id] = ctx.author
    msg = await ctx.send(f"🔍 Fast searching: `{query}`...")

    try:
        if wavelink.Pool.nodes:
            try:
                player: wavelink.Player = wavelink.Pool.get_player(ctx.guild.id)
                if not player:
                    raise Exception("No player")
            except:
                try:
                    player = await ctx.author.voice.channel.connect(self_deaf=True)
                except:
                    player = wavelink.Pool.get_player(ctx.guild.id)

            tracks = await wavelink.Playable.search(query)
            if not tracks:
                tracks = await wavelink.Playable.search(f"ytsearch:{query}")

            if tracks:
                track = tracks[0]
                await player.play(track)
                embed = discord.Embed(title="🎧 Now Playing - Playing Inside VC, Showing Outside Chat", description=f"**{track.title}**", color=0x00FF00)
                if hasattr(track, 'artwork') and track.artwork:
                    embed.set_thumbnail(url=track.artwork)
                embed.add_field(name="Speed", value="⚡ 1-2 sec - Best Node", inline=True)
                embed.add_field(name="Autoplay", value="ON" if autoplay_state.get(ctx.guild.id) else "OFF", inline=True)
                embed.set_footer(text=f"Requested by {ctx.author} | Cloudie 🎧 | APP + Slash")
                try:
                    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=track.title[:30]))
                except:
                    pass
                await msg.delete()
                await _start_live_music_panel(ctx.guild.id, player, channel=ctx.channel)
                return
    except Exception as e:
        print(f"Lavalink fast failed: {e}, falling back to FFmpeg...")

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch1:{query}", download=False))
        if 'entries' in data:
            data = data['entries'][0]
        
        audio_url = data.get('url')
        if not audio_url:
            webpage = data.get('webpage_url')
            if webpage:
                fresh = await loop.run_in_executor(None, lambda: ytdl.extract_info(webpage, download=False))
                audio_url = fresh.get('url')
                data = fresh
        
        if not audio_url:
            raise Exception("Audio URL not found! Update yt-dlp")

        vc = ctx.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            get_queue(ctx.guild.id).append(data)
            embed = discord.Embed(title="Added to Queue 📜", description=f"**{data.get('title')}**", color=0xFFA500)
            if data.get('thumbnail'):
                embed.set_thumbnail(url=data.get('thumbnail'))
            embed.add_field(name="Position", value=f"#{len(get_queue(ctx.guild.id))} in queue", inline=True)
            await msg.delete()
            return await ctx.send(embed=embed, view=MusicView())

        source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTS)
        player_ff = YTDLSource(source, data=data)
        ffmpeg_now_playing[ctx.guild.id] = data
        autoplay_history[ctx.guild.id].add(data.get('title','').lower())
        vc.play(player_ff, after=get_after_callback(ctx.guild.id))
        embed = discord.Embed(title="🎧 Now Playing - Inside VC Playing, Outside Display", description=f"**{data.get('title')}**", color=0xC9A7F5)
        if data.get('thumbnail'):
            embed.set_thumbnail(url=data.get('thumbnail'))
        embed.add_field(name="Uploader", value=data.get('uploader', 'Unknown')[:50], inline=True)
        duration = data.get('duration', 0)
        if duration:
            embed.add_field(name="Duration", value=f"{duration//60}:{duration%60:02d}", inline=True)
        embed.add_field(name="Autoplay", value="ON" if autoplay_state.get(ctx.guild.id) else "OFF", inline=True)
        embed.set_footer(text=f"Requested by {ctx.author} | Cloudie 🎧 | Fast Search OP")
        try:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=data.get("title","Music")[:30]))
        except:
            pass
        await msg.delete()
        await ctx.send(embed=embed, view=MusicView())
    except Exception as e:
        await msg.delete()
        await ctx.send(f"Error: {e}\nTry direct YouTube link!")
        print(f"Play error: {e}")

@bot.command(name="pause")
async def pause_cmd(ctx):
    player: wavelink.Player = ctx.voice_client
    if not player or not player.playing:
        return await ctx.send("Nothing playing.")
    await player.pause(not player.paused)
    status = "Paused" if player.paused else "Resumed"
    await ctx.send(f"{status}.")

@bot.command(name="resume")
async def resume_cmd(ctx):
    player: wavelink.Player = ctx.voice_client
    if not player:
        return await ctx.send("Not in VC.")
    await player.pause(False)
    await ctx.send("Resumed.")

@bot.command(name="skip", aliases=["next", "s"])
async def skip_cmd(ctx):
    player: wavelink.Player = ctx.voice_client
    if not player or not player.playing:
        # Try FFmpeg
        vc = ctx.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            return await ctx.send("Skipped FFmpeg track.")
        return await ctx.send("Nothing playing.")
    await player.skip(force=True)
    await ctx.send("Skipped.")

@bot.command(name="stop")
async def stop_cmd(ctx):
    player: wavelink.Player = ctx.voice_client
    if not player:
        vc = ctx.voice_client
        if vc:
            twentyfour_seven[ctx.guild.id] = False
            save_247()
            get_queue(ctx.guild.id).clear()
            if vc.is_playing() or vc.is_paused():
                vc.stop()
            await vc.disconnect()
            return await ctx.send("Stopped and left VC.")
        return await ctx.send("Not in VC.")
    twentyfour_seven[ctx.guild.id] = False
    save_247()
    player.queue.clear()
    await player.stop()
    await ctx.send("Stopped.")

@bot.command(name="queue", aliases=["q"])
async def queue_cmd(ctx):
    # Check both wavelink and FFmpeg queue
    player: wavelink.Player = ctx.voice_client
    if player and hasattr(player, 'queue') and not player.queue.is_empty:
        queue_list = list(player.queue)[:15]
        desc = ""
        for i, track in enumerate(queue_list, 1):
            desc += f"{i}. {track.title[:45]} - {track.author}\n"
        embed = discord.Embed(title=f"Queue - {len(player.queue)} tracks (Lavalink)", description=desc, color=0xC9A7F5)
        await ctx.send(embed=embed, view=MusicView())
    else:
        q = get_queue(ctx.guild.id)
        if not q:
            return await ctx.send("Queue is empty. Use /play to add songs. Autoplay will play different songs if ON.")
        desc = ""
        for i, data in enumerate(q[:15], 1):
            desc += f"{i}. {data.get('title','Unknown')[:45]} - {data.get('uploader','Unknown')}\n"
        embed = discord.Embed(title=f"Queue - {len(q)} tracks (FFmpeg)", description=desc, color=0xC9A7F5)
        await ctx.send(embed=embed, view=MusicView())

@bot.command(name="nowplaying", aliases=["np", "now"])
async def nowplaying_cmd(ctx):
    # Try wavelink first
    player: wavelink.Player = ctx.voice_client
    if player and player.current:
        track = player.current
        embed = discord.Embed(title="Now Playing", color=0x00FF00)
        embed.set_thumbnail(url=track.artwork or bot.user.display_avatar.url)
        embed.add_field(name="Song", value=f"{track.title}", inline=False)
        embed.add_field(name="Artist", value=f"{track.author}", inline=True)
        await ctx.send(content=f"# 🎵 {track.title}\nby {track.author}", embed=embed, view=MusicView())
    else:
        data = ffmpeg_now_playing.get(ctx.guild.id)
        if not data:
            return await ctx.send("Nothing playing. Use /play")
        embed = discord.Embed(title="🎧 Now Playing - Inside Playing Outside Shown", description=f"**{data.get('title')}**", color=0xC9A7F5)
        if data.get('thumbnail'): embed.set_thumbnail(url=data.get('thumbnail'))
        embed.add_field(name="Uploader", value=data.get('uploader','Unknown'), inline=True)
        await ctx.send(embed=embed, view=MusicView())

@bot.command(name="volume", aliases=["vol"])
async def volume_cmd(ctx, vol: int = None):
    player: wavelink.Player = ctx.voice_client
    if not player:
        return await ctx.send("Not in VC.")
    if vol is None:
        return await ctx.send(f"Volume: {player.volume}% Use {PREFIX}volume <0-100>")
    if vol < 0 or vol > 100:
        return await ctx.send("Volume 0-100.")
    await player.set_volume(vol)
    await ctx.send(f"Volume set to {vol}%.")

@bot.command(name="autoplay", aliases=["ap"])
async def autoplay_cmd(ctx):
    gid = ctx.guild.id
    autoplay_state[gid] = not autoplay_state[gid]
    save_autoplay()
    status = "ON" if autoplay_state[gid] else "OFF"
    await ctx.send(f"🔁 Autoplay: {status} - Will play different songs automatically when queue ends!")

@bot.command(name="247", aliases=["24/7", "stay"])
async def twentyfour_cmd(ctx):
    gid = ctx.guild.id
    twentyfour_seven[gid] = not twentyfour_seven[gid]
    save_247()
    await ctx.send(f"🔒 24/7: {'ON' if twentyfour_seven[gid] else 'OFF'} - Bot will stay in VC")

@bot.command(name="restart")
async def restart_cmd(ctx):
    if not is_owner(ctx): return await ctx.send("Only owner can restart.")
    await ctx.send("Restarting bot... 🔄")
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.command(name="shutdown", aliases=["band", "stopbot"])
async def shutdown_cmd(ctx):
    if not is_owner(ctx): return await ctx.send("Only owner can shutdown.")
    await ctx.send("Shutting down... 👋")
    await bot.close()

@bot.command(name="help", aliases=["commands", "h"])
async def help_cmd(ctx):
    pages = []
    def page(title, number, body):
        e = discord.Embed(title=f"✦ CLOUDIE • PREMIUM | {title}", description=body, color=0xE7D6FF)
        e.set_footer(text=f"Cloudie • Premium Bot 🎧 • Page {number} | Prefix: {PREFIX} | Slash: / | APP + Supports Commands ✅")
        return e

    pages.append(page("01 • MUSIC - FAST SEARCH OP", 1, f"""**🎵 Fast Music - Local Host + Premium Nodes - ALL OLD COMMANDS KEPT**
{PREFIX}play <song> • {PREFIX}join • {PREFIX}leave • {PREFIX}disconnect
{PREFIX}pause • {PREFIX}resume • {PREFIX}skip • {PREFIX}stop
{PREFIX}queue • {PREFIX}nowplaying • {PREFIX}np • {PREFIX}volume 0-100
{PREFIX}autoplay • {PREFIX}247 • {PREFIX}stay
🎵 **Lavalink:** Public Lavalink v4 nodes (configured in lavalink_nodes.json)
🎧 **FFmpeg:** Ultra fast reconnect + 128k
🔁 **Autoplay:** Different songs auto
🏷️ **APP + Supports Commands**"""))
    pages.append(page("02 • MODERATION - ALL OLD", 2, f"""**🛡️ All Old Mod Commands - Updated**
{PREFIX}ban @user <reason> - Ban with DM embed
{PREFIX}kick @user <reason> - Kick with DM
{PREFIX}mute @user [minutes] <reason> • {PREFIX}timeout
{PREFIX}unmute @user
{PREFIX}warn @user <reason> • {PREFIX}warnings @user • {PREFIX}warns
{PREFIX}clear [1-100] • {PREFIX}purge
{PREFIX}nick @user <nickname> - Change nick
**DM:** Member gets full embed DM if DMs open"""))
    pages.append(page("03 • CHANNEL - ALL OLD", 3, f"""**🔒 All Channel Commands - Kept**
{PREFIX}lock • {PREFIX}unlock - Lock/unlock send
{PREFIX}hide • {PREFIX}unhide - Hide/view
{PREFIX}slowmode <seconds> - Set slowmode
{PREFIX}nuke - Clone + delete channel (premium nuke)
Permissions checked"""))
    pages.append(page("04 • AUTOMOD - OLD + NEW", 4, f"""**🛡️ Old AutoMod + New Punishment Page**
{PREFIX}automod - Shows premium panel with buttons 💣🚫🔠🤬🔗📢🛡️
{PREFIX}automod <feature> on/off
{PREFIX}automod punishment <feature> <ban/kick/mute/warn/delete>
{PREFIX}automod panel
{PREFIX}fban on/off - Fake name ban
{PREFIX}nickban on/off/add/remove/list
{PREFIX}addbadword <word> • {PREFIX}removebadword <word> • {PREFIX}badwordlist
**Old badwords + nickban kept!**
**New:** antinuke, antispam, anticaps, antibadword, antilink, antiinvite, antieveryone, antiraid - Each with custom punishment!"""))
    pages.append(page("05 • ANTINUKE - NEW PREMIUM", 5, f"""**💣 AntiNuke - Advanced Protection - NEW**
{PREFIX}antinuke - Shows full config + panel
{PREFIX}antinuke on/off
{PREFIX}antinuke punishment <ban/kick/mute>
{PREFIX}antinuke whitelist add/remove <@user>
{PREFIX}antinuke log #channel
{PREFIX}antinuke panel - Interactive buttons
**Protects:** Channel delete/create, Role delete/create, Mass ban/kick, Bot add
**Log + Punish + Whitelist**"""))
    pages.append(page("06 • AUTORESPONDER - OLD KEPT", 6, f"""**💬 Old AR System - Fully Kept**
{PREFIX}ar - List all
{PREFIX}ar add <trigger> <response>
{PREFIX}ar remove <trigger>
{PREFIX}ar list • {PREFIX}ar clear
{PREFIX}autoresponder - Same as ar
JSON save - autoresponder.json"""))
    pages.append(page("07 • WELCOME - PREMIUM MENU NEW", 7, f"""**👋 PREMIUM Greet Menu - New Update**
{PREFIX}greet - Opens PREMIUM menu with buttons:
  • Set Channel 📢
  • Set Message 💬 - Modal with {{user}} {{server}} {{count}}
  • Set Title 📝 - Embed title modal
  • Set Description 📄 - Embed desc modal
  • Set Image Link 🖼️ - Modal: image URL + thumb URL (link se)
  • Set Color 🎨 - Hex #00FF00 modal
  • Toggle Embed ✨ ON/OFF
  • Toggle ON/OFF 🔴
  • Test Greet 🧪 - Sends to channel
  • Preview 👁️ - Preview embed

{PREFIX}setgreet #channel
{PREFIX}greetconfig message/title/description/color/thumbnail/image/embed
**Embed Link Support:** Direct image URL se embed lagta hai!
**All old welcome kept + premium menu!**"""))
    pages.append(page("08 • TICKET - OLD + EMBED NEW", 8, f"""**🎫 Old Ticket + New Embed Customization**
{PREFIX}ticket - Shows config + panel
{PREFIX}ticket panel - Sends panel with button
{PREFIX}ticket title <title>
{PREFIX}ticket description <desc>
{PREFIX}ticket color <#hex>
{PREFIX}ticket button <label>
{PREFIX}close - Close ticket (in ticket channel)
{PREFIX}add @user - Add user to ticket
{PREFIX}remove @user - Remove user
**Old ticket system kept + new embed config!**"""))
    pages.append(page("09 • UTILITY - ALL OLD KEPT", 9, f"""**📊 All Old Utility - Kept + Fake Ping**
{PREFIX}ping - Fake 50-99ms Excellent (kept ✅) + real ping hidden
{PREFIX}pingboost - Same fake ping panel
{PREFIX}network - 6 lavalink nodes info + fast search
{PREFIX}avatar @user • {PREFIX}av
{PREFIX}serverinfo • {PREFIX}si - Shows AntiNuke + AutoMod count
{PREFIX}userinfo • {PREFIX}ui • {PREFIX}whois
{PREFIX}help • {PREFIX}commands • {PREFIX}h - This premium paginator
**All old utility commands kept!**"""))
    if is_owner(ctx):
        pages.append(page("10 • OWNER - ALL OLD", 10, f"""**👑 Owner Only - {OWNER_ID} - Old Kept**
{PREFIX}restart - Restart bot
{PREFIX}shutdown • {PREFIX}band • {PREFIX}stopbot - Shutdown
Owner can use without prefix: restart / shutdown
**All systems premium:**
• Music OP ⚡ 6 nodes + FFmpeg
• AutoMod + AntiNuke 💣 14 features
• Greet Premium 👋 Link embed + message
• Ticket Embed 🎫
• Fake Ping 50-90ms ✅ Kept
• Prefix: {PREFIX} • Slash: / • APP + Supports Commands
• YouTube + Google fast search
• All old !help commands migrated to {PREFIX}help!"""))
    else:
        pages.append(page("10 • PREMIUM INFO", 10, f"""**✨ Cloudie Premium - All Old Commands Migrated**
**Old !help had:** Music, Mod, Channel, AutoMod, AR, Greet, Ticket, Utility, Owner
**New {PREFIX}help has:** SAME + NEW:
• Music OP (6 nodes)
• Mod (ban/kick/mute/warn/clear/nick)
• Channel (lock/unlock/hide/slowmode/nuke)
• AutoMod (14 features + punishment)
• AntiNuke (new)
• AR (old kept)
• Greet Premium Menu (link embed + msg)
• Ticket Embed
• Utility + Fake Ping kept
• Owner

**All old commands kept, nothing deleted!**
**Prefix:** {PREFIX} (was !) • **Slash:** / • **Tags:** APP + Supports Commands ✅"""))

    view = HelpPaginator(pages)
    view.update_labels()
    await ctx.send(embed=pages[0], view=view)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        return await ctx.send("❌ You don't have permission to use this command.", delete_after=5)
    if isinstance(error, commands.BotMissingPermissions):
        return await ctx.send("❌ Cloudie is missing a required Discord permission.", delete_after=5)
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send(f"❌ Missing argument: {error.param.name}. Use {PREFIX}help.", delete_after=6)
    if isinstance(error, commands.BadArgument):
        return await ctx.send("❌ Invalid argument. Check the user/channel/number and try again.", delete_after=6)
    original = getattr(error, "original", error)
    print(f"Command error in {getattr(ctx.command, 'qualified_name', 'unknown')}: {original}")
    try:
        await ctx.send("❌ Something went wrong while running that command.", delete_after=6)
    except Exception:
        pass

# ===================== SLASH COMMANDS - SUPPORTS COMMANDS TAG =====================
@bot.event
async def on_ready():
    # Clear old broken slash commands first
    try:
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        for g in bot.guilds:
            try:
                bot.tree.clear_commands(guild=g)
                await bot.tree.sync(guild=g)
            except: pass
    except: pass
    # Now sync fresh working commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands - FIXED - No more 'App not respond'")
    except Exception as e:
        print(f"Sync failed: {e}")
    print(f"ONLINE {bot.user} | Prefix: {PREFIX} | {len(bot.guilds)} servers | Greet+Automod14+Ticket+Help Restored")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{PREFIX}help | Premium Full"))

# Lavalink setup is installed as the real Bot.setup_hook below.
@bot.tree.command(name="ping", description="📊 Check bot ping - Real ping")
async def ping_slash(interaction: discord.Interaction):
    ws_ping = round(bot.latency * 1000) if bot.latency else 0
    embed = discord.Embed(color=0x2ECC71)
    embed.description = f"""## 📊 Pong! - Real Ping
🛰️ WebSocket: {ws_ping}ms Real
💾 Database: Real
🎵 Lavalink: {len(NODE_CONFIGS)} configured public nodes
⏰ Uptime: {int((time.time()-START_TIME)//3600)} hours
━━━━━━━━━━━━━━━━━━━━━━
✦ Cloudie • Premium Bot 🎧 | No fake"""
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="play", description="🎵 Play a song - Fast search OP")
@app_commands.describe(query="Song name or YouTube link - Fast YouTube + Google search")
async def play_slash(interaction: discord.Interaction, query: str):
    if not interaction.user.voice:
        return await interaction.response.send_message("Join a VC first! Use /join", ephemeral=True)
    await interaction.response.defer()
    try:
        if not interaction.guild.voice_client:
            await interaction.user.voice.channel.connect(self_deaf=True)
        last_text_channel[interaction.guild.id] = interaction.channel.id
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch1:{query}", download=False))
        if 'entries' in data:
            data = data['entries'][0]
        audio_url = data.get('url')
        if not audio_url:
            webpage = data.get('webpage_url')
            if webpage:
                fresh = await loop.run_in_executor(None, lambda: ytdl.extract_info(webpage, download=False))
                audio_url = fresh.get('url')
                data = fresh
        vc = interaction.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            get_queue(interaction.guild.id).append(data)
            embed = discord.Embed(title="Added to Queue 📜", description=f"**{data.get('title')}**", color=0xFFA500)
            if data.get('thumbnail'): embed.set_thumbnail(url=data.get('thumbnail'))
            return await interaction.followup.send(embed=embed, view=MusicView())
        source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTS)
        player_ff = YTDLSource(source, data=data)
        ffmpeg_now_playing[interaction.guild.id] = data
        autoplay_history[interaction.guild.id].add(data.get('title','').lower())
        vc.play(player_ff, after=get_after_callback(interaction.guild.id))
        try: await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=data.get('title','')[:30]))
        except: pass
        embed = discord.Embed(title="Now Playing 🎧 (Slash - Fast)", description=f"**{data.get('title')}**", color=0xC9A7F5)
        if data.get('thumbnail'): embed.set_thumbnail(url=data.get('thumbnail'))
        embed.set_footer(text=f"Requested by {interaction.user} | Cloudie 🎧 | OP Search")
        await interaction.followup.send(embed=embed, view=MusicView())
    except Exception as e:
        await interaction.followup.send(f"Error: {e}")

@bot.tree.command(name="join", description="🔊 Join your voice channel - Fixed")
async def join_slash(interaction: discord.Interaction):
    if not interaction.user.voice:
        return await interaction.response.send_message("You are not in a voice channel.", ephemeral=True)
    channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client
    if vc:
        await vc.move_to(channel)
        await interaction.response.send_message(f"Moved to {channel.mention}")
    else:
        new_vc = await channel.connect(self_deaf=True)
        if hasattr(new_vc, "set_volume"):
            try: await new_vc.set_volume(100)
            except: pass
        await interaction.response.send_message(f"Joined {channel.mention}")

@bot.tree.command(name="help", description="📖 Show all commands - English full update")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="✦ CLOUDIE • PREMIUM | HELP - V10 English Full", description=f"**Music OP:** /play <song> • /join • /leave • /pause • /skip\n**Mod:** /ban • /kick • /mute • /warn • /clear\n**AutoMod New:** /automod panel - AntiNuke, AntiSpam, AntiCaps, AntiBadWord, AntiLink\n**Greet:** Fully customizable embed with {{user}} placeholders\n**Ticket:** Custom embed support\n**Prefix:** {PREFIX} • **Slash:** / • **Tags:** APP + Supports Commands\n**Fake Ping:** Kept ✅ 50-90ms\n**Fast Search:** Local host + 6 nodes = OP", color=0xC9A7F5)
    embed.set_footer(text="Cloudie • Premium Bot 🎧 | One number update ✌️")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="autoplay", description="🔁 Toggle autoplay - plays different songs automatically")
async def autoplay_slash(interaction: discord.Interaction):
    gid = interaction.guild.id
    autoplay_state[gid] = not autoplay_state[gid]
    save_autoplay()
    status = "ON" if autoplay_state[gid] else "OFF"
    await interaction.response.send_message(f"🔁 Autoplay: {status} - Will play different songs automatically!")

@bot.tree.command(name="automod", description="🛡️ Open AutoMod panel - AntiNuke, AntiSpam, AntiCaps, AntiBadWord")
async def automod_slash(interaction: discord.Interaction):
    cfg = automod_config[interaction.guild.id]
    pun = automod_punishment[interaction.guild.id]
    desc = ""
    for k,v in cfg.items():
        if k in ["fban", "nickban"]: continue
        desc += f"**{k}:** {'🟢 ON' if v else '🔴 OFF'} | Punish: `{pun.get(k, 'delete')}`\n"
    embed = discord.Embed(title="🛡️ AutoMod Panel - Full Control", description=desc[:4000], color=0xC9A7F5)
    view = AutomodView(interaction.guild.id)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="antinuke", description="💣 AntiNuke control - Protect server from nukes")
async def antinuke_slash(interaction: discord.Interaction):
    cfg = antinuke_config[interaction.guild.id]
    embed = discord.Embed(title="💣 AntiNuke System", description=f"**Status:** {'🟢 ON' if cfg['enabled'] else '🔴 OFF'}\n**Punishment:** `{cfg['punishment']}`\n**Whitelist:** {len(cfg['whitelist'])} users\nUse {PREFIX}antinuke on/off, punishment, whitelist add/remove", color=0xFF0000)
    view = AutomodView(interaction.guild.id)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="greet", description="☁️ Greet system - pastel setup menu")
async def welcome_slash(interaction: discord.Interaction):
    cfg = welcome_config[interaction.guild.id]
    view = WelcomeSetupView(interaction.guild.id)
    embed = view.get_embed()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="ban", description="🔨 Ban a member - Old command kept")
@app_commands.describe(member="Member to ban", reason="Reason for ban")
@commands.has_permissions(ban_members=True)
async def ban_slash(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await interaction.response.defer()
    try:
        dm_success, _ = await dm_user(member, "Banned", interaction.guild, reason, None, interaction.user)
        await member.ban(reason=f"{reason} | By {interaction.user}")
        embed = discord.Embed(title="Member Banned", color=0xFF0000)
        embed.add_field(name="User", value=f"{member} ({member.id})")
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="DM", value="Sent" if dm_success else "Failed")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"Failed: {e}", ephemeral=True)

@bot.tree.command(name="kick", description="👢 Kick a member - Old command kept")
@app_commands.describe(member="Member to kick", reason="Reason")
async def kick_slash(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await interaction.response.defer()
    try:
        await member.kick(reason=reason)
        await interaction.followup.send(f"{member} kicked. Reason: {reason}")
    except Exception as e:
        await interaction.followup.send(f"Failed: {e}", ephemeral=True)

@bot.tree.command(name="clear", description="🧹 Clear messages - Old command kept")
@app_commands.describe(amount="Amount 1-100")
async def clear_slash(interaction: discord.Interaction, amount: int = 5):
    if amount < 1 or amount > 100:
        return await interaction.response.send_message("Amount 1-100", ephemeral=True)
    await interaction.response.defer()
    try:
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted {len(deleted)} messages", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Failed: {e}", ephemeral=True)

@bot.tree.command(name="serverinfo", description="📊 Server info - Old command kept")
async def serverinfo_slash(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=guild.name, color=0xE7D6FF)
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Security", value=f"AntiNuke: {'ON' if antinuke_config[guild.id]['enabled'] else 'OFF'}")
    embed.set_footer(text=f"ID: {guild.id} | Prefix: {PREFIX} | Premium")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ticket", description="🎫 Ticket system - Old + new embed")
async def ticket_slash(interaction: discord.Interaction):
    cfg = ticket_config[interaction.guild.id]
    embed = discord.Embed(title=cfg["embed_title"], description=cfg["embed_description"], color=cfg["embed_color"])
    await interaction.response.send_message(embed=embed, view=TicketView())


# ===================== CLOUDIE REBUILD: PERSISTENT MUSIC SERVICES =====================
# 24/7 sessions are stored per guild as {guild_id: {enabled, channel_id}}.
# Legacy boolean entries are migrated safely; enabled entries without a channel
# cannot be restored and are reported instead of guessing a destination.
import tempfile
from discord.ext import tasks

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
TWENTYFOUR_FILE = os.path.join(DATA_DIR, "twentyfour.json")
PANELS_FILE = os.path.join(DATA_DIR, "music_panels.json")
_voice_reconnect_tasks = {}
_voice_reconnect_locks = defaultdict(asyncio.Lock)
_panel_refresh_tasks = {}
_panel_refs = {}
_music_filters = defaultdict(lambda: "reset")
_loop_state = defaultdict(bool)

def _atomic_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".cloudie-", suffix=".json", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=2)
            fp.flush()
            os.fsync(fp.fileno())
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def _read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as fp:
            value = json.load(fp)
        return value if isinstance(value, type(default)) else default
    except (OSError, ValueError, TypeError):
        return default

def _load_247_sessions():
    raw = _read_json(TWENTYFOUR_FILE, {})
    sessions = {}
    changed = False
    for key, value in raw.items():
        try:
            gid = int(key)
        except (TypeError, ValueError):
            changed = True
            continue
        if isinstance(value, dict):
            enabled = bool(value.get("enabled", False))
            channel_id = value.get("channel_id")
        else:  # old Cloudie format only saved a boolean, not a channel
            enabled, channel_id = bool(value), None
            changed = True
        if enabled and channel_id:
            sessions[str(gid)] = {"enabled": True, "channel_id": int(channel_id)}
        elif enabled:
            sessions[str(gid)] = {"enabled": True, "channel_id": None}
        if not enabled:
            changed = True
    if changed:
        _atomic_json(TWENTYFOUR_FILE, sessions)
    return sessions

_247_sessions = _load_247_sessions()

def _save_247_sessions():
    _atomic_json(TWENTYFOUR_FILE, _247_sessions)
    # Keep the original in-memory flag in sync for existing music/idle handlers.
    for key, item in _247_sessions.items():
        twentyfour_seven[int(key)] = bool(item.get("enabled"))

def _247_enabled(guild_id):
    item = _247_sessions.get(str(guild_id), {})
    return bool(item.get("enabled") and item.get("channel_id"))

def _247_channel_id(guild_id):
    item = _247_sessions.get(str(guild_id), {})
    return item.get("channel_id") if item.get("enabled") else None

def _set_247(guild_id, enabled, channel_id=None):
    if enabled:
        _247_sessions[str(guild_id)] = {"enabled": True, "channel_id": int(channel_id)}
        twentyfour_seven[guild_id] = True
    else:
        _247_sessions.pop(str(guild_id), None)
        twentyfour_seven[guild_id] = False
    _save_247_sessions()

def _load_panel_refs():
    raw = _read_json(PANELS_FILE, {})
    for key, value in raw.items():
        try:
            if isinstance(value, dict) and value.get("channel_id") and value.get("message_id"):
                _panel_refs[int(key)] = (int(value["channel_id"]), int(value["message_id"]))
        except (TypeError, ValueError):
            continue

_load_panel_refs()

async def _get_or_fetch_panel(guild_id):
    ref = _panel_refs.get(guild_id)
    if not ref:
        return None
    channel_id, message_id = ref
    channel = bot.get_channel(channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return None
    try:
        return await channel.fetch_message(message_id)
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        return None

async def _cloudie_refresh_panel(guild_id, player=None, channel=None):
    player = player or (bot.get_guild(guild_id).voice_client if bot.get_guild(guild_id) else None)
    if not isinstance(player, wavelink.Player):
        return
    embed = _live_music_embed(player, guild_id)
    message = await _get_or_fetch_panel(guild_id)
    if message:
        try:
            await message.edit(embed=embed, view=MusicView())
            live_music_messages[guild_id] = message
            return
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            _panel_refs.pop(guild_id, None)
    if channel is None:
        channel_id = last_text_channel.get(guild_id)
        channel = bot.get_channel(channel_id) if channel_id else None
    if channel is None:
        return
    try:
        message = await channel.send(embed=embed, view=MusicView())
        live_music_messages[guild_id] = message
        _panel_refs[guild_id] = (channel.id, message.id)
        _atomic_json(PANELS_FILE, {
            str(gid): {"channel_id": ch, "message_id": msg}
            for gid, (ch, msg) in _panel_refs.items()
        })
    except (discord.Forbidden, discord.HTTPException) as exc:
        print(f"[Cloudie Panel] Cannot create panel for guild {guild_id}: {exc}")

async def _cloudie_panel_loop(guild_id):
    try:
        while True:
            await asyncio.sleep(15)
            guild = bot.get_guild(guild_id)
            player = guild.voice_client if guild else None
            if not isinstance(player, wavelink.Player) or not player.current:
                break
            await _cloudie_refresh_panel(guild_id, player)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        print(f"[Cloudie Panel] Refresh error for {guild_id}: {exc}")
    finally:
        _panel_refresh_tasks.pop(guild_id, None)

async def _cloudie_start_panel(guild_id, player, channel=None):
    await _cloudie_refresh_panel(guild_id, player, channel)
    old = _panel_refresh_tasks.get(guild_id)
    if old and not old.done():
        old.cancel()
    _panel_refresh_tasks[guild_id] = asyncio.create_task(_cloudie_panel_loop(guild_id))

async def _connect_247_guild(guild_id):
    async with _voice_reconnect_locks[guild_id]:
        if not _247_enabled(guild_id):
            return False
        guild = bot.get_guild(guild_id)
        if guild is None:
            print(f"[Cloudie 24/7] Guild {guild_id} is not available in cache; will retry on next READY.")
            return False
        channel_id = _247_channel_id(guild_id)
        channel = guild.get_channel(channel_id) if channel_id else None
        if channel is None:
            print(f"[Cloudie 24/7] Saved voice channel {channel_id} is missing in {guild_id}; disabling stale session.")
            _set_247(guild_id, False)
            return False
        me = guild.me
        perms = channel.permissions_for(me) if me else None
        if not perms or not perms.connect or not perms.speak:
            print(f"[Cloudie 24/7] Missing Connect/Speak permission in #{channel.name} ({guild_id}); session kept for a later READY.")
            return False
        existing = guild.voice_client
        if existing and getattr(existing, "channel", None):
            if existing.channel.id == channel.id:
                return True
            try:
                await existing.move_to(channel)
                return True
            except (discord.Forbidden, discord.HTTPException) as exc:
                print(f"[Cloudie 24/7] Move failed in {guild_id}: {exc}")
                return False
        for attempt in range(1, 6):
            if not _247_enabled(guild_id):
                return False
            try:
                await channel.connect(cls=wavelink.Player, self_deaf=True, timeout=20, reconnect=True)
                print(f"[Cloudie 24/7] Reconnected to #{channel.name} in {guild.name}.")
                return True
            except (discord.Forbidden, discord.NotFound) as exc:
                print(f"[Cloudie 24/7] Cannot join channel in {guild_id}: {exc}")
                return False
            except Exception as exc:
                delay = min(60, 2 ** attempt)
                print(f"[Cloudie 24/7] Attempt {attempt}/5 failed in {guild_id}: {exc}; retry in {delay}s.")
                if attempt < 5:
                    await asyncio.sleep(delay)
        return False

async def _schedule_247_reconnect(guild_id, delay=0):
    if not _247_enabled(guild_id):
        return
    old = _voice_reconnect_tasks.get(guild_id)
    if old and not old.done():
        return
    async def runner():
        try:
            if delay:
                await asyncio.sleep(delay)
            await _connect_247_guild(guild_id)
        finally:
            _voice_reconnect_tasks.pop(guild_id, None)
    _voice_reconnect_tasks[guild_id] = asyncio.create_task(runner())

async def _restore_247_sessions():
    await bot.wait_until_ready()
    await asyncio.sleep(3)
    for key, item in list(_247_sessions.items()):
        gid = int(key)
        if item.get("enabled") and item.get("channel_id"):
            await _schedule_247_reconnect(gid, 0)
        elif item.get("enabled"):
            print(f"[Cloudie 24/7] Guild {gid} has legacy ON state but no saved channel; use !247 while in voice to reconfigure.")

async def _cloudie_voice_state_listener(member, before, after):
    if not bot.user or member.id != bot.user.id:
        return
    guild_id = member.guild.id
    if before.channel and not after.channel and _247_enabled(guild_id):
        await _schedule_247_reconnect(guild_id, 5)
    elif after.channel and _247_enabled(guild_id):
        # Keep the persisted channel aligned only when Cloudie is in the saved channel.
        if after.channel.id == _247_channel_id(guild_id):
            return

# Use Wavelink's server-side Lavalink filters; failures are surfaced to the user.
async def _apply_cloudie_filter(player, key):
    if key == "reset":
        filters = wavelink.Filters()
    elif key == "nightcore":
        filters = wavelink.Filters(timescale=wavelink.Timescale(speed=1.25, pitch=1.12, rate=1.0))
    elif key == "8d":
        filters = wavelink.Filters(rotation=wavelink.Rotation(rotation_hz=0.18))
    elif key == "karaoke":
        filters = wavelink.Filters(karaoke=wavelink.Karaoke(level=1.0, mono_level=1.0, filter_band=220.0, filter_width=100.0))
    elif key == "bassboost":
        bands = [wavelink.EqualizerBand(band=i, gain=g) for i, g in enumerate(
            [0.18, 0.16, 0.13, 0.10, 0.06, 0.02] + [0.0] * 9
        )]
        filters = wavelink.Filters(equalizer=wavelink.Equalizer(bands=bands))
    else:
        raise ValueError("Unknown filter")
    await player.set_filters(filters=filters)
    _music_filters[player.guild.id] = key

class CloudieFilterSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Bassboost", value="bassboost", description="Boost low frequencies"),
            discord.SelectOption(label="Nightcore", value="nightcore", description="Faster tempo and higher pitch"),
            discord.SelectOption(label="8D Audio", value="8d", description="Rotating stereo effect"),
            discord.SelectOption(label="Karaoke", value="karaoke", description="Reduce centered vocals"),
            discord.SelectOption(label="Reset", value="reset", description="Clear all audio filters"),
        ]
        super().__init__(placeholder="Choose an audio filter", min_values=1, max_values=1, options=options)
    async def callback(self, interaction):
        player = interaction.guild.voice_client if interaction.guild else None
        if not isinstance(player, wavelink.Player):
            return await interaction.response.send_message("Lavalink playback is not active.", ephemeral=True)
        try:
            await _apply_cloudie_filter(player, self.values[0])
            await interaction.response.send_message(f"Filter applied: **{self.values[0]}**", ephemeral=True)
            await _cloudie_refresh_panel(interaction.guild.id, player)
        except Exception as exc:
            await interaction.response.send_message(f"Filter could not be applied by the current Lavalink node: `{exc}`", ephemeral=True)

class CloudieFilterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(CloudieFilterSelect())

# Replace the original ephemeral-only toggle with per-server durable channel persistence.
async def _cloudie_247_command(ctx):
    if not ctx.guild:
        return await ctx.send("This command is available in a server.")
    gid = ctx.guild.id
    if _247_enabled(gid):
        _set_247(gid, False)
        await ctx.send(embed=discord.Embed(
            title="24/7 mode disabled",
            description="Cloudie will no longer reconnect automatically in this server.",
            color=0xDCCBFA
        ))
        return
    if not ctx.author.voice or not ctx.author.voice.channel:
        return await ctx.send("Join the voice channel you want Cloudie to stay in, then run `!247`.")
    channel = ctx.author.voice.channel
    perms = channel.permissions_for(ctx.guild.me)
    if not perms.connect or not perms.speak:
        return await ctx.send("I need **Connect** and **Speak** permissions in that voice channel.")
    try:
        if ctx.guild.voice_client:
            if ctx.guild.voice_client.channel.id != channel.id:
                await ctx.guild.voice_client.move_to(channel)
        else:
            await channel.connect(cls=wavelink.Player, self_deaf=True, timeout=20, reconnect=True)
        _set_247(gid, True, channel.id)
        await ctx.send(embed=discord.Embed(
            title="24/7 mode enabled",
            description=f"Saved voice channel: {channel.mention}\nCloudie will restore this server's voice session after a restart.",
            color=0xDCCBFA
        ))
    except Exception as exc:
        return await ctx.send(f"Could not join `{channel.name}`: `{exc}`")


@bot.command(name="loop", aliases=["repeat"])
async def cloudie_loop_command(ctx, mode: str = None):
    player = ctx.guild.voice_client if ctx.guild else None
    if not isinstance(player, wavelink.Player):
        return await ctx.send("Lavalink playback is not active.")
    if mode and mode.lower() in ("off", "disable", "none"):
        enabled = False
    elif mode and mode.lower() in ("on", "track", "current"):
        enabled = True
    else:
        enabled = not _loop_state[ctx.guild.id]
    try:
        player.queue.mode = wavelink.QueueMode.loop if enabled else wavelink.QueueMode.normal
        _loop_state[ctx.guild.id] = enabled
        await ctx.send(f"Track loop {'enabled' if enabled else 'disabled'}.")
        await _cloudie_refresh_panel(ctx.guild.id, player)
    except Exception as exc:
        await ctx.send(f"Loop could not be changed: `{exc}`")

# Override the old command callback without registering a duplicate command.
try:
    bot.get_command("247").callback = _cloudie_247_command
except Exception as exc:
    print(f"[Cloudie 24/7] Could not replace command callback: {exc}")

# Voice state event listener is separate from the bot's existing event handlers.
bot.add_listener(_cloudie_voice_state_listener, "on_voice_state_update")

# Patch the old panel helpers to use stored message IDs, avoiding duplicate panels.
_refresh_live_music_panel = _cloudie_refresh_panel
_start_live_music_panel = _cloudie_start_panel


# Consistent pastel panel with requester and playback metadata.
def _live_music_embed(player, guild_id):
    track = getattr(player, "current", None)
    if not track:
        return discord.Embed(title="Cloudie | Music Player", description="Nothing is playing.", color=0xDCCBFA)
    duration = int(getattr(track, "length", 0) or 0)
    position = int(getattr(player, "position", 0) or 0)
    if duration:
        ratio = min(1.0, position / duration)
        filled = min(18, int(ratio * 18))
        progress = f"`{_live_time(position)}` {'▰' * filled}{'▱' * (18-filled)} `{_live_time(duration)}`"
    else:
        progress = "`LIVE`"
    title = str(getattr(track, "title", "Unknown track"))[:220]
    artist = str(getattr(track, "author", "Unknown artist"))[:100]
    uri = getattr(track, "uri", None)
    embed = discord.Embed(
        title="Cloudie | Now Playing",
        description=(f"**[{title}]({uri})**" if uri else f"**{title}**") + f"\n**Artist:** {artist}\n\n{progress}",
        color=0xDCCBFA
    )
    artwork = getattr(track, "artwork", None)
    if artwork:
        embed.set_thumbnail(url=artwork)
    requester_text = str(last_requester.get(guild_id) or "Unknown")[:100]
    embed.add_field(name="Requester", value=requester_text[:100], inline=True)
    embed.add_field(name="Status", value="Paused" if getattr(player, "paused", False) else "Playing", inline=True)
    embed.add_field(name="Volume", value=f"{getattr(player, 'volume', 100)}%", inline=True)
    embed.add_field(name="Loop", value="Track" if _loop_state.get(guild_id, False) else "Off", inline=True)
    embed.add_field(name="Autoplay", value="On" if autoplay_state.get(guild_id, False) else "Off", inline=True)
    embed.add_field(name="24/7", value="On" if _247_enabled(guild_id) else "Off", inline=True)
    embed.set_footer(text=f"Cloudie • Filter: {_music_filters[guild_id]} • Updates every 15 seconds")
    return embed

class MusicView(discord.ui.View):
    """Persistent server music controls. All buttons use stable custom IDs."""
    def __init__(self):
        super().__init__(timeout=None)

    async def _player(self, interaction):
        return interaction.guild.voice_client if interaction.guild else None

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.secondary, custom_id="cloudie:pause", row=0)
    async def pause_button(self, interaction, button):
        player = await self._player(interaction)
        if isinstance(player, wavelink.Player) and player.playing:
            await player.pause(True)
        elif player and player.is_playing():
            player.pause()
        else:
            return await interaction.response.send_message("Nothing is playing.", ephemeral=True)
        await interaction.response.send_message("Paused.", ephemeral=True)
        if isinstance(player, wavelink.Player):
            await _cloudie_refresh_panel(interaction.guild.id, player)

    @discord.ui.button(label="Resume", style=discord.ButtonStyle.success, custom_id="cloudie:resume", row=0)
    async def resume_button(self, interaction, button):
        player = await self._player(interaction)
        if isinstance(player, wavelink.Player) and player.paused:
            await player.pause(False)
        elif player and player.is_paused():
            player.resume()
        else:
            return await interaction.response.send_message("Playback is not paused.", ephemeral=True)
        await interaction.response.send_message("Resumed.", ephemeral=True)
        if isinstance(player, wavelink.Player):
            await _cloudie_refresh_panel(interaction.guild.id, player)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary, custom_id="cloudie:skip", row=0)
    async def skip_button(self, interaction, button):
        player = await self._player(interaction)
        if isinstance(player, wavelink.Player) and player.playing:
            await player.skip(force=True)
        elif player and (player.is_playing() or player.is_paused()):
            player.stop()
        else:
            return await interaction.response.send_message("Nothing is playing.", ephemeral=True)
        await interaction.response.send_message("Skipped.", ephemeral=True)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, custom_id="cloudie:stop", row=0)
    async def stop_button(self, interaction, button):
        player = await self._player(interaction)
        if isinstance(player, wavelink.Player):
            player.queue.clear()
            await player.stop()
            await _cloudie_refresh_panel(interaction.guild.id, player)
        elif player:
            get_queue(interaction.guild.id).clear()
            if player.is_playing() or player.is_paused():
                player.stop()
        else:
            return await interaction.response.send_message("Cloudie is not connected.", ephemeral=True)
        await interaction.response.send_message("Playback stopped and queue cleared.", ephemeral=True)

    @discord.ui.button(label="Queue", style=discord.ButtonStyle.secondary, custom_id="cloudie:queue", row=1)
    async def queue_button(self, interaction, button):
        player = await self._player(interaction)
        if isinstance(player, wavelink.Player):
            try:
                tracks = list(player.queue)[:15]
            except Exception:
                tracks = []
            description = "\n".join(f"`{i}.` **{track.title[:70]}** — {track.author}" for i, track in enumerate(tracks, 1))
        else:
            tracks = get_queue(interaction.guild.id)
            description = "\n".join(f"`{i}.` **{item.get('title', 'Unknown')[:70]}** — {item.get('uploader', 'Unknown')}" for i, item in enumerate(tracks[:15], 1))
        if not tracks:
            return await interaction.response.send_message("Queue is empty.", ephemeral=True)
        await interaction.response.send_message(embed=discord.Embed(title="Cloudie | Queue", description=description, color=0xDCCBFA), ephemeral=True)

    @discord.ui.button(label="Autoplay", style=discord.ButtonStyle.secondary, custom_id="cloudie:autoplay", row=1)
    async def autoplay_button(self, interaction, button):
        gid = interaction.guild.id
        autoplay_state[gid] = not autoplay_state.get(gid, False)
        save_autoplay()
        await interaction.response.send_message(f"Autoplay {'enabled' if autoplay_state[gid] else 'disabled'}.", ephemeral=True)
        player = await self._player(interaction)
        if isinstance(player, wavelink.Player):
            await _cloudie_refresh_panel(gid, player)

    @discord.ui.button(label="24/7", style=discord.ButtonStyle.secondary, custom_id="cloudie:247", row=1)
    async def stay_button(self, interaction, button):
        gid = interaction.guild.id
        if _247_enabled(gid):
            _set_247(gid, False)
            await interaction.response.send_message("24/7 disabled for this server.", ephemeral=True)
            return
        member = interaction.user
        if not member.voice or not member.voice.channel:
            return await interaction.response.send_message("Join a voice channel first, then press 24/7.", ephemeral=True)
        channel = member.voice.channel
        perms = channel.permissions_for(interaction.guild.me)
        if not perms.connect or not perms.speak:
            return await interaction.response.send_message("I need Connect and Speak permissions in that channel.", ephemeral=True)
        try:
            current = interaction.guild.voice_client
            if current:
                if current.channel.id != channel.id:
                    await current.move_to(channel)
            else:
                await channel.connect(cls=wavelink.Player, self_deaf=True, timeout=20, reconnect=True)
            _set_247(gid, True, channel.id)
            await interaction.response.send_message(f"24/7 enabled. Saved {channel.mention} for restart recovery.", ephemeral=True)
        except Exception as exc:
            await interaction.response.send_message(f"Could not enable 24/7: `{exc}`", ephemeral=True)

    @discord.ui.button(label="Filters", style=discord.ButtonStyle.secondary, custom_id="cloudie:filters", row=2)
    async def filters_button(self, interaction, button):
        await interaction.response.send_message("Choose a Lavalink audio filter:", view=CloudieFilterView(), ephemeral=True)


# Register persistent controls and connect Lavalink from the real discord.py setup_hook.
async def _cloudie_setup_hook():
    try:
        bot.add_view(MusicView())
        bot.add_view(MentionView())
        bot.add_view(TicketView())
    except Exception as exc:
        print(f"[Cloudie] Persistent view setup warning: {exc}")
    nodes = []
    for config in NODE_CONFIGS:
        try:
            nodes.append(wavelink.Node(
                identifier=config["identifier"], uri=config["uri"],
                password=config["password"], retries=None, resume_timeout=120
            ))
        except Exception as exc:
            print(f"[Cloudie Lavalink] Invalid node config ({config.get('identifier', 'unknown')}): {exc}")
    connected = 0
    if nodes:
        try:
            await wavelink.Pool.connect(nodes=nodes, client=bot)
            connected = len(nodes)
            for node in nodes:
                print(f"[Cloudie Lavalink] Node registered: {node.identifier}")
        except Exception as exc:
            print(f"[Cloudie Lavalink] Node pool connection failed: {exc}")
    print(f"[Cloudie Lavalink] Registered {connected}/{len(NODE_CONFIGS)} configured nodes.")

bot.setup_hook = _cloudie_setup_hook

# Restore sessions only after the gateway has supplied guild/channel caches.
_original_on_ready = bot.on_ready
async def _cloudie_on_ready():
    await _original_on_ready()
    if not getattr(bot, "_cloudie_restore_started", False):
        bot._cloudie_restore_started = True
        asyncio.create_task(_restore_247_sessions())
bot.on_ready = _cloudie_on_ready


if not TOKEN or TOKEN == "PUT_YOUR_BOT_TOKEN_HERE_IN_token.txt_FILE":
    raise RuntimeError("Bot token missing. Put the token in token.txt before starting Cloudie.")
bot.run(TOKEN)
