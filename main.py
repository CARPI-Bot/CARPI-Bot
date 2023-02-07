import platform
import os
import discord
from discord.ext import commands
from globals import *
from cogs import calculator, gavin, modtools

TOKEN = open("TOKEN.txt").read()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, owner_ids=OWNER_IDS, intents=intents)

@bot.event
async def on_ready():
    await bot.add_cog(calculator.Calculator(bot))
    await bot.add_cog(gavin.Gavin(bot))
    await bot.add_cog(modtools.Moderator(bot))
    print(f"Logged in as {bot.user.name}#{bot.user.discriminator}")
    print(f"Python version {platform.python_version()}")
    print(f"Discord.py version {discord.__version__}")

def main():
    bot.run(TOKEN)
    
if __name__ == "__main__":
    main()