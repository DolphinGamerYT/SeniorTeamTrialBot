import discord
from datetime import datetime
color_main = 0xA430C0
color_red = 0xFF0000


def hex_to_rgb(value: str):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def hex_to_colour(hex: str) -> discord.Colour:
    r, g, b = hex_to_rgb(hex)
    return discord.Colour.from_rgb(r, g, b)


async def send_error_embed(channel: discord.TextChannel, title, description):
    embed = discord.Embed(title=title, description=description,
                          timestamp=datetime.utcnow(), color=color_red)
    return await channel.send(embed=embed)


async def edit_error_embed(message: discord.Message, title, description):
    embed = discord.Embed(title=title, description=description,
                          timestamp=datetime.utcnow(), color=color_red)
    return await message.edit(embed=embed)


async def send_embed(channel: discord.TextChannel, title, description):
    embed = discord.Embed(title=title, description=description,
                          timestamp=datetime.utcnow(), color=color_main)
    return await channel.send(embed=embed)


async def send_embed_no_footer(channel: discord.TextChannel, title, description):
    embed = discord.Embed(
        title=title, description=description, color=color_main)
    return await channel.send(embed=embed)


async def edit_embed(message: discord.Message, title, description):
    embed = discord.Embed(title=title, description=description,
                          timestamp=datetime.utcnow(), color=color_main)
    return await message.edit(content="", embed=embed)


async def send_embed_file(channel: discord.TextChannel, title, description, file: discord.File):
    embed = discord.Embed(title=title, description=description,
                          timestamp=datetime.utcnow(), color=color_main)
    return await channel.send(embed=embed, file=file)


def generate_embed(title, description) -> discord.Embed:
    embed = discord.Embed(title=title, description=description,
                          timestamp=datetime.utcnow(), color=color_main)
    return embed
