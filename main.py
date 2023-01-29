import platform
import discord
from discord.ext import commands
from globals import *

TOKEN = open("TOKEN.txt").read()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, owner_ids=OWNER_IDS, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator}\n'\
    f'Python version {platform.python_version()}\n'\
    f'Discord.py version {discord.__version__}')

def main():
    bot.run(TOKEN)
    
if __name__ == "__main__":
    main()