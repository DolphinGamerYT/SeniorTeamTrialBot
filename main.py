import discord
import json
import codecs
from discord.ext import commands

from modules import utils

cogs = ['cogs.error_handler', 'cogs.music']


class Bot(commands.AutoShardedBot):

    def __init__(self):
        with codecs.open(f"config.json", "r", "utf-8") as f:
            config = json.load(f)
            self.token = config["token"]
            self.prefix = config["prefix"]
            self.color = utils.hex_to_colour(config["color"])
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=self.prefix, case_insensitive=True, intents=intents)

        self.devs = [
            310011769332695041
        ]

    async def on_ready(self):
        print(f"{self.user.name} | {self.user.id} is online!")


bot = Bot()
bot.remove_command('help')


async def startup_task():
    await bot.wait_until_ready()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your music!"))
    print("Loading cogs...")
    for cog in cogs:
        try:
            bot.load_extension(cog)
            print(f"Loaded {cog}")
        except Exception as e:
            print(e)
    print("Cogs loaded!")


@bot.command()
async def reload(ctx, cog=None):
    if ctx.author.id not in bot.devs:
        return
    if not cog:
        for j in range(len(cogs)):
            cog = cogs[j]
            try:
                bot.reload_extension(cog)
                await ctx.send(f"**{j+1}/{len(cogs)}**: Reloaded {cog}")
            except Exception as e:
                await ctx.send(f"**{j+1}/{len(cogs)}**: {cog}: {e}")
    else:
        try:
            bot.reload_extension(cog)
            await ctx.send(F"Reloaded {cog}")
        except Exception as e:
            await ctx.send(f"{cog}: {e}")


if __name__ == '__main__':
    bot.loop.create_task(startup_task())
    bot.run(bot.token)
