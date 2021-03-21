from asyncio import tasks
import discord
import re
import codecs
import json
from discord.ext import commands, task
from datetime import datetime

import main


class Moderation(commands.Cog):

    def __init__(self, bot: main.Bot):
        self.bot = bot
        with codecs.open(f"config.json", "r", "utf-8") as f:
            config = json.load(f)
            self.blacklist = config["blacklist"]
            log_channel_id = config["log_channel"]
            muted_role_id = config["muted_role"]

        self.log_channel = discord.utils.find(
            bot.get_all_channels, id=log_channel_id)
        self.muted_role = discord.utils.find(
            self.log_channel.guild.roles, id=muted_role_id)

        self.mutes = self.bot.database.get_mutes()

    @task.loop(minutes=1)
    async def mute_task(self):
        time_now = datetime.utcnow()
        timestamp_now = datetime.timestamp(time_now)

        for mute in self.mutes:
            if datetime.timestamp(mute["created"]) + mute["duration"] <= timestamp_now:
                await self._remove_mute(mute["user"])

    async def _remove_mute(self, user_id: int):
        for x in range(0, len(self.mutes)):
            if self.mutes[x]["user"] == user_id:
                self.mutes.pop(x)
                break

        await self.bot.database.remove_mute(user_id)

        user = await self.log_channel.guild.get_member(user_id)
        if user is not None:
            await user.remove_roles(self.muted_role)

        embed = discord.Embed(
            title="New Umute", color=self.bot.color, timestamp=datetime.utcnow())
        embed.add_field(name="User unmuted",
                        value=f"<@{user_id}>", inline=True)
        embed.add_field(name="User unmuted ID",
                        value=f"`{user_id}`", inline=True)

        await self.log_channel.send(embed=embed)

    async def _add_mute(self, user: discord.Member, reason: str, duration: int, staff: discord.Member):
        mute_data = await self.bot.database.add_mute(user, reason, duration, staff)
        if duration is not None and duration != 0:
            self.mutes.append(mute_data)

        await user.add_roles(self.muted_role)

        embed = discord.Embed(
            title="New Mute", color=self.bot.color, timestamp=datetime.utcnow())
        embed.add_field(name="User muted",
                        value=f"{user.mention}", inline=True)
        embed.add_field(name="User muted ID",
                        value=f"`{user.id}`", inline=True)
        embed.add_field(name="Staff", value=f"{staff.mention}", inline=True)

        if duration is not None and duration != 0:
            embed.add_field(name="Duration",
                            value=f"`{duration}`", inline=True)
        else:
            embed.add_field(name="Duration", value=f"Permanent", inline=True)

        embed.add_field(name="Reason", value=f"{user.mention}", inline=True)

        await self.log_channel.send(embed=embed)

    async def _add_ban(self, user: discord.Member, reason: str, staff: discord.Member):
        await self.bot.database.add_ban(user, reason, staff)

        await user.ban(reason=reason)

        embed = discord.Embed(
            title="New Ban", color=self.bot.color, timestamp=datetime.utcnow())
        embed.add_field(name="User banned",
                        value=f"{user.mention}", inline=True)
        embed.add_field(name="User banned ID",
                        value=f"`{user.id}`", inline=True)
        embed.add_field(name="Staff", value=f"{staff.mention}", inline=True)

        embed.add_field(name="Reason", value=f"{user.mention}", inline=True)

        await self.log_channel.send(embed=embed)

    async def _add_kick(self, user: discord.Member, reason: str, staff: discord.Member):
        await self.bot.database.add_kick(user, reason, staff)

        await user.kick(reason=reason)

        embed = discord.Embed(
            title="New Kick", color=self.bot.color, timestamp=datetime.utcnow())
        embed.add_field(name="User kicked",
                        value=f"{user.mention}", inline=True)
        embed.add_field(name="User kicked ID",
                        value=f"`{user.id}`", inline=True)
        embed.add_field(name="Staff", value=f"{staff.mention}", inline=True)

        embed.add_field(name="Reason", value=f"{user.mention}", inline=True)

        await self.log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.guild_permissions.administrator:
            for regex in self.blacklist:
                if len(re.findall(regex, message.content)) != 0:
                    return await message.delete()


def setup(bot):
    bot.add_cog(Moderation(bot))
