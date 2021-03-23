import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.core import command

import main
from modules import utils

raw_commands_data = [
    {
        "name": "Core",
        "commands": [
            {
                "format": "ping",
                "description": "Get the bot's ping"
            }
        ]
    },
    {
        "name": "Music",
        "commands": [
            {
                "format": "join",
                "description": "Adds/moves the bot to your voice channel."
            },
            {
                "format": "leave",
                "description": "Removes the bot from the voice channel."
            },
            {
                "format": "pause",
                "description": "Pause the music."
            },
            {
                "format": "play <url>",
                "description": "Add a song to the queue. If the queue is empty, it will start playing it."
            },
            {
                "format": "np",
                "description": "Info of the song playing."
            },
            {
                "format": "queue",
                "description": "Check the queue of songs."
            },
            {
                "format": "skip",
                "description": "Skip the playing song."
            },
        ]
    },
    {
        "name": "Moderation",
        "commands": [
            {
                "format": "ban <@user> [reason]",
                "description": "Ban a user from the server."
            },
            {
                "format": "kick <@user> [reason]",
                "description": "Kick a user from the server."
            },
            {
                "format": "mute <@user> [reason]",
                "description": "Mute permanently a user."
            },
            {
                "format": "tempmute <@user> <duration in minutes> [reason]",
                "description": "Mute temporally a user."
            },
            {
                "format": "unmute <@user>",
                "description": "Unmute a user."
            },
        ]
    }
]


class Core(commands.Cog):

    def __init__(self, bot: main.Bot):
        self.bot = bot

    async def get_command(self, content):
        for _commands in raw_commands_data:
            for command in _commands["commands"]:
                if command["format"].split(" ")[0] in content:
                    return command["format"]
        return None

    @commands.command(name="ping")
    async def _ping(self, ctx):
        await ctx.send(f'Pong! In `{round(self.bot.latency * 1000)}ms`')

    @commands.command(name="help")
    async def _help(self, ctx):
        embed = discord.Embed(
            title="All Commands", color=self.bot.color, timestamp=datetime.utcnow())

        for commands_data in raw_commands_data:
            line = ""
            for command in commands_data["commands"]:
                line += "`{}{}` -> {}\n".format(self.bot.prefix,
                                                command["format"], command["description"])

            embed.add_field(
                name=commands_data["name"], value=line, inline=False)

        await ctx.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, commands.NoPrivateMessage):
            await utils.send_error_embed(ctx.channel, "Invalid Usage", "This command can only be used on guilds.")
        elif isinstance(error, commands.PrivateMessageOnly):
            await utils.send_error_embed(ctx.channel, "Invalid Usage", "This command can only be used on DMs.")
        elif isinstance(error, commands.MissingRequiredArgument):
            format_ = await self.get_command(ctx.message.content)
            if format_ is None:
                return await utils.send_error_embed(ctx.channel, "Invalid Arguments", "Please, use the correct arguments")
            await utils.send_error_embed(ctx.channel, "Invalid Arguments", "Please, use this command as following: `{}{}`".format(self.bot.prefix, format_))
        elif isinstance(error, commands.MemberNotFound):
            await utils.send_error_embed(ctx.channel, "Invalid Arguments", "User is invalid or wasn't found.")
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, commands.MissingAnyRole):
            await utils.send_error_embed(ctx.channel, "No Permissions", "You don't have the right permissions to run this command.")
        else:
            raise error


def setup(bot):
    bot.add_cog(Core(bot))
