import youtube_dl as yt
import discord

YTDL_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist"
}


def get_video(url):
    return yt.YoutubeDL(YTDL_OPTS).extract_info(url, download=False)
