import asyncio
import os
import discord
from discord.ext import commands
from globals import *

TOKEN = open("TOKEN.txt").read()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=COMMAND_PREFIX, owner_ids=OWNER_IDS, intents=intents)

async def loadCogs():
    for fileName in os.listdir('./cogs'):
        if fileName.endswith('.py'):
            await bot.load_extension(f"cogs.{fileName[:-3]}")

@bot.event
async def on_ready():
    print("=================================")
    print(f"Logged in as {bot.user.name}#{bot.user.discriminator}")
    print(f"Discord.py version {discord.__version__}")
    print("=================================")
    print(f"Currently deployed in {len(bot.guilds)} guild(s):\n")
    for guild in bot.guilds:
        print(guild.name)
    print("=================================")

async def main():
    await loadCogs()
    await bot.start(TOKEN)
    
if __name__ == "__main__":
    asyncio.run(main())