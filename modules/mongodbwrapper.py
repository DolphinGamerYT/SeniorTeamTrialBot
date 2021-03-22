import pymongo
import discord
import json
import codecs
import datetime
from datetime import datetime


class Database:

    def __init__(self) -> None:
        with codecs.open(f"config.json", "r", "utf-8") as f:
            config = json.load(f)
            url = config["mongodb"]["mongodb_url"]
            database = config["mongodb"]["mongodb_database"]
        self.client = pymongo.MongoClient(url)

        if database in self.client.list_database_names():
            self.db = self.client[database]
            print("Database Connected!")
        else:
            print("The database specified in the config does not exist!\n")
            input("Press enter to exit...")
            quit()

        self.bans = self.db["bans"]
        self.kicks = self.db["kicks"]
        self.mutes = self.db["mutes"]

    async def add_mute(self, user: discord.Member, reason: str, duration: int, staff_member: discord.Member) -> dict:
        mute_data = {"user": user.id, "reason": reason,
                     "created": datetime.utcnow(), "valid": True, "duration": duration, "staff": staff_member.id}

        self.mutes.insert_one(mute_data)
        return mute_data

    async def is_muted(self, user: discord.Member) -> bool:
        return self.mutes.find_one({"user": user.id, "valid": True}) is not None

    async def remove_mute(self, user_id: int):
        self.mutes.find_one_and_update({"user": user_id, "valid": True}, {
                                       "$set": {"unmuted": datetime.utcnow(), "valid": False}})

    def get_mutes(self) -> list:
        mutes = self.mutes.find({"valid": True})
        mutes_data = list()

        for mute in mutes:
            if mute["duration"] is not None and mute["duration"] != 0:
                mutes_data.append(mute)

        return mutes_data

    async def add_ban(self, user: discord.Member, reason: str, staff_member: discord.Member):
        ban_data = {"user": user.id, "reason": reason,
                    "created": datetime.utcnow(), "staff": staff_member.id}
        self.bans.insert_one(ban_data)

    async def add_kick(self, user: discord.Member, reason: str, staff_member: discord.Member):
        kick_data = {"user": user.id, "reason": reason,
                     "created": datetime.utcnow(), "staff": staff_member.id}
        self.kicks.insert_one(kick_data)
