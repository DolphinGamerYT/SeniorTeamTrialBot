import discord
import math
import asyncio
from discord.ext import commands
from datetime import datetime

import main
from modules import utils, youtube


def add_zero(num):
    if int(num) <= 9:
        return "0" + str(num)
    return num


async def in_voice_channel(ctx):
    voice = ctx.author.voice
    bot_voice = ctx.guild.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    await utils.send_error_embed(ctx.channel, "Error", "I'm not in a voice channel")
    return False


async def audio_playing(ctx):
    client = ctx.guild.voice_client
    if client and client.channel and client.source:
        return True
    await utils.send_error_embed(ctx.channel, "Error", "Not currently playing any audio.")
    return False


class Music(commands.Cog):

    def __init__(self, bot: main.Bot):
        self.bot = bot
        self.guilds = dict()

    def get_state(self, guild: discord.Guild):
        if guild.id not in self.guilds:
            return GuildInfo(guild.id)
        return self.guilds[guild.id]

    @commands.command(name="join")
    @commands.guild_only()
    async def _join(self, ctx):
        if ctx.author.voice is not None and ctx.author.voice.channel is not None:
            channel = ctx.author.voice.channel
            client = await channel.connect()
            self.get_state(ctx.guild)

            embed = discord.Embed(
                title="Voice Connected", description=f"Joined the voice channel `{channel}`.", color=self.bot.green_color, timestamp=datetime.utcnow())
            embed.set_footer(
                text=f"Requested by: {ctx.author}", icon_url=f"{ctx.author.avatar_url}")
            return await ctx.channel.send(embed=embed)

        return await utils.send_error_embed(ctx.channel, "Invalid Channel", "You need to be in a voice channel for me to join!")

    @commands.command(name="leave", aliases=["stop", "quit"])
    @commands.guild_only()
    @commands.check(in_voice_channel)
    async def _leave(self, ctx):
        message = await ctx.channel.send(embed=discord.Embed(title="Leaving voice channel...", color=0xff0000))

        client = ctx.guild.voice_client
        if client and client.channel:
            await client.disconnect()
        if ctx.guild.id in self.guilds:
            del self.guilds[ctx.guild.id]

        embed = discord.Embed(
            title="Channel Left", description="I left the voice channel that I was in.", color=self.bot.green_color, timestamp=datetime.utcnow())
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=f"{ctx.author.avatar_url}")
        await message.edit(embed=embed)

    @commands.command(name="pause", aliases=["resume"])
    @commands.guild_only()
    @commands.check(in_voice_channel)
    @commands.check(audio_playing)
    async def _pause(self, ctx):
        client = ctx.guild.voice_client
        if client.is_paused():
            client.resume()
            embed = discord.Embed(title="Playing music", description="The music has been resumed back.",
                                  color=self.bot.color, timestamp=datetime.utcnow())
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.channel.send(embed=embed)
        else:
            client.pause()
            embed = discord.Embed(title="Music paused", description=f"The music has been paused. Use `{self.bot.prefix}resume` to continue playing the music.",
                                  color=self.bot.color, timestamp=datetime.utcnow())
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.channel.send(embed=embed)

    def _play_song(self, client, state, song):
        state.playing = state.queue.pop(0)
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url, executable="C:/bin/ffmpeg.exe"), volume=state.volume/100)

        def after_playing(err):
            if len(state.queue) > 0:
                next_song = state.queue.pop(0)
                self._play_song(client, state, next_song)
            else:
                asyncio.run_coroutine_threadsafe(client.disconnect(),
                                                 self.bot.loop)

        client.play(source, after=after_playing)

    @commands.command(name="play")
    @commands.guild_only()
    @commands.check(in_voice_channel)
    async def _play(self, ctx, *, url):
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)

        try:
            video = youtube.get_video(url)
        except Exception as e:
            await utils.send_error_embed(ctx.channel, "Invalid URL", "The URL you have entered is not a valid video.")
            return

        song = Song(video)
        state.queue.append(song)

        embed = song.get_embed()
        embed.color = self.bot.color
        embed.title = "Added to the queue"
        await ctx.channel.send(embed=embed)

        if state.playing is None:
            self._play_song(client, state, song)

    @commands.command(name="playing", aliases=["np", "nowplaying"])
    @commands.guild_only()
    @commands.check(in_voice_channel)
    @commands.check(audio_playing)
    @commands.command(name="playing", aliases=["np", "nowplaying"])
    async def _playing(self, ctx):
        state = self.get_state(ctx.guild)
        if state.playing is None:
            return await utils.send_error_embed(ctx.channel, "Nothing playing", "There isn't any song playing right now.")

        embed = state.playing.get_embed()
        embed.color = self.bot.color
        embed.title = "Now playing"
        await ctx.channel.send(embed=embed)


class GuildInfo:

    def __init__(self, guild_id) -> None:
        self.guild_id = guild_id

        self.playing = None
        self.queue = list()
        self.volume = 100

    def get_queue_paged(self, page):
        max_pages = math.ceil(len(self.queue)/10)-1
        if page > max_pages:
            page = max_pages
        elif page < 0:
            page = 0

        paged_queue = [self.queue[i:i+4]
                       for i in range(0, len(self.queue), 10)]
        return paged_queue[page]


class Song:

    def __init__(self, info) -> None:
        self.title = info["title"]
        self.thumbnail = info["thumbnail"]
        # self.description = info["description"]

        self.channel_name = info["uploader"]
        self.channel_url = info["channel_url"]
        self.url = info["webpage_url"]

        self.duration = info["duration"]
        self.stream_url = info["url"]

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Song details", description=f"Now playing: ```{self.title}```")

        embed.add_field(name="Title", value=f"[{self.title}]({self.url})")
        embed.add_field(
            name="Author", value=f"[{self.channel_name}]({self.channel_url})")

        song_duration = datetime.fromtimestamp(self.duration)
        embed.add_field(
            name="Duration", value=f"{add_zero(song_duration.minute)}:{add_zero(song_duration.second)}")

        embed.set_thumbnail(url=self.thumbnail)
        return embed


def setup(bot):
    bot.add_cog(Music(bot))
