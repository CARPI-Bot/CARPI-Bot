import os
import sys
import json
import logging

import discord
from discord.ext import commands

Context = commands.Context

async def sendUnknownError(ctx: Context, error: commands.errors = None) -> None:
    """
    Standard error message for use in local command error listeners,
    only for production use. It will not help with debugging, since
    the point is to mask the actual error.
    """
    embed_var = discord.Embed(
        title = ERROR_TITLE,
        description = "Unknown error. Contact an admin for more details.",
        color = 0xC80000
    )
    await ctx.send(embed=embed_var)
    if (error is not None):
        logging.error(f'Command "{ctx.command}" in extension "{ctx.cog.qualified_name}": {error}')

def getAbsPath(rel_path: str) -> str:
    """
    Given a relative path, returns a unix-friendly absolute path,
    or the absolute path to the temp folder created by PyInstaller's
    bootloader.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("./")
    return os.path.join(base_path, rel_path).replace("\\", "/")

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
# This should not be referenced outside of the main file
TOKEN = config["token"]

# Your bot's command prefix
# Consider using commands.Bot.command_prefix instead
CMD_PREFIX = config["prefix"]

# Your bot's login credentials to the MySQL database
SQL_LOGIN = config["sql_login"]

# For use in temporary messages
DEL_DELAY = 3

# For use in error handlers
ERROR_TITLE = "Something went wrong."
NO_PERM_MSG = "You don't have permissions to do that."
BAD_MEMBER_MSG = "Member not found. Nicknames and usernames are case sensitive, or maybe you spelled it wrong?"