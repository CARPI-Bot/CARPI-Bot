import os
import sys
import json
import logging
import discord
from discord.ext import commands

Context = commands.Context

# The standard error message that should send upon a command error, only for production
# use though. It will not help you with debugging, since its point is to mask the actual
# error using a fun-looking embed.
async def sendUnknownError(ctx:Context, error:commands.errors=None) -> None:
    embed_var = discord.Embed(
        title=ERROR_TITLE,
        description="Unknown error. Contact an admin for more details.",
        color=0xC80000
    )
    await ctx.send(embed=embed_var)
    if (error != None):
        logging.error(f"Command \"{ctx.command}\" in cog \"{ctx.cog.qualified_name}\": {error}")

# Given a relative path, returns its absolute path equivalent, or the absolute path to
# the temp folder created by PyInstaller's bootloader. Necessary if this project is to
# be compiled into a one-file build.
def getResourcePath(rel_path:str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("./")
    # Returns a Unix-friendly path using only forward slashes
    return os.path.join(base_path, rel_path).replace("\\", "/")

# Directory containing discord.py cogs
cogs_dir_rel_path = "./cogs"

# For use in commands that check for owner status
OWNER_IDS = {
    230003732836909056, # Raymond
    298223516262596608, # Anthony
    310864184923652107, # Edwin
    455125448884748308, # Jack
}

with open("config.json", "r") as infile:
    config = json.load(infile)

# Your bot's token
TOKEN = config["token"]

# Your bot's command prefix
COMMAND_PREFIX = config["prefix"]

# Your bot's login credentials to the MySQL database
SQL_LOGIN = config["sql_login"]

# The SQL schema your bot should target
SQL_SCHEMA = config["sql_schema"]

# For use in temporary messages
DEL_DELAY = 3

# For use in error handlers
ERROR_TITLE = "Something went wrong."
NO_PERM_MSG = "You don't have permissions to do that."
BAD_MEMBER_MSG = "Member not found. Nicknames and usernames are case sensitive, or maybe you spelled it wrong?"