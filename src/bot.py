import os
import discord
from discord.ext import commands
from globals import *

async def load_extensions(path:str, bot:commands.Bot):
    for file_name in os.listdir(path):
        new_path = os.path.join(path, file_name)
        if os.path.isdir(new_path):
            await load_extensions(os.path.join(new_path), bot)
        else:
            if file_name.endswith(".py"):
                try: await bot.load_extension(f"cogs.{file_name[:-3]}")
                except: pass

class Bot(commands.Bot):

    def __init__(self, prefix:str, intents:discord.Intents):
        super().__init__(command_prefix=prefix, intents=intents)
        self.token = open("TOKEN.txt").read().strip()

    async def setup_hook(self):
        await load_extensions("./cogs", self)
    
    async def on_ready(self):
        num_synced = len(await self.tree.sync())
        print("==================================")
        print(">>" + f"Logged in as {self.user.name}#{self.user.discriminator}".center(30) + "<<")
        print(">>" + f"Discord.py version {discord.__version__}".center(30) + "<<")
        print(f"{num_synced} command(s) synced!".center(34))
        print("==================================\n")
        print(f"Currently deployed in {len(self.guilds)} guild(s):")
        for guild in self.guilds:
            print(" - " + guild.name)
        print("\n==================================")