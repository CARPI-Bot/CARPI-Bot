import asyncio
import discord
from discord.ext import commands
from globals import *
import os

TOKEN = open("TOKEN.txt").read().strip()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=COMMAND_PREFIX, owner_ids=OWNER_IDS, intents=intents)

async def loadCogs(bot:commands.Bot):
    for file_name in os.listdir('./cogs'):
        if file_name.endswith('.py'):
            await bot.load_extension(f"cogs.{file_name[:-3]}")

@bot.event
async def on_ready():
    num_synced = len(await bot.tree.sync())
    print("==================================")
    print(">>" + f"Logged in as {bot.user.name}#{bot.user.discriminator}".center(30) + "<<")
    print(">>" + f"Discord.py version {discord.__version__}".center(30) + "<<")
    print(f"{num_synced} command(s) synced!".center(34))
    print("==================================\n")
    print(f"Currently deployed in {len(bot.guilds)} guild(s):")
    for guild in bot.guilds:
        print(" - " + guild.name)
    print("\n==================================")

async def main():
    await loadCogs(bot)
    await bot.start(TOKEN)
    
if __name__ == "__main__":
    asyncio.run(main())