import os
import discord
from discord.ext import commands
from globals import *

# Must take in a directory (folder), path cannot be a simple file
async def load_cogs(path:str, bot:commands.Bot):
    for file_name in os.listdir(path):
        new_path = os.path.join(path, file_name)
        if os.path.isdir(new_path):
            await load_cogs(new_path, bot)
        else:
            if file_name.endswith(".py"):
                cog = new_path[2:-3].replace("\\", ".")
                try: await bot.load_extension(cog)
                except commands.NoEntryPointError:
                    print(f"\n{cog} has no 'setup' function, ignoring file.")
                except Exception as err:
                    print(f"\n{err}")
                else: bot.loaded_cogs.append(cog)

class Bot(commands.Bot):

    def __init__(self, prefix:str, intents:discord.Intents):
        super().__init__(command_prefix=prefix, intents=intents)
        self.token = open("TOKEN.txt").read().strip()
        self.loaded_cogs = []

    async def setup_hook(self):
        await load_cogs(".\src\cogs", self)
    
    async def on_ready(self):
        num_synced = len(await self.tree.sync())
        print("\n==================================")
        print(">>" + f"Logged in as {self.user.name}#{self.user.discriminator}".center(30) + "<<")
        print(">>" + f"Discord.py version {discord.__version__}".center(30) + "<<")
        print(f"{num_synced} command(s) synced!".center(34))
        print("==================================\n")
        print(f"{len(self.loaded_cogs)} file(s) successfully loaded:")
        for cog in self.loaded_cogs: print(f"- {cog}")
        print("\n==================================\n")
        print(f"Currently deployed in {len(self.guilds)} guild(s):")
        for guild in self.guilds: print(f" - {guild.name}")
        print("\n==================================")