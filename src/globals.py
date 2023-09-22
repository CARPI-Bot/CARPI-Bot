import os
import sys
import discord
from discord.ext.commands import Context

# The standard error message that should send upon a command error, only for production
# use though. It will not help you with debugging, since its point is to mask the actual
# error using a fun-looking embed.
async def sendDefaultError(ctx:Context) -> None:
    embed_var = discord.Embed(
        title=ERROR_TITLE,
        description="Unknown error. Contact an admin for more details.",
        color=0xC80000
    )
    embed_var.set_footer(text=f"\u200bCommand attempted by {ctx.author.name}")
    await ctx.send(embed=embed_var)

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

# Given a relative path, reads the text file at the location and returns its contents
# while performing a few sanity checks along the way.
def readTextFile(rel_path:str) -> str:
    content = ""
    abs_path = getResourcePath(rel_path)
    try:
        with open(abs_path) as file:
            content = file.read().strip("\n\r ")
        if len(content) == 0:
            raise
    except:
        print(f"[ERROR] Can't open \"{abs_path}\", path is invalid or file is empty.")
        sys.exit(1)
    return content

# Text file containing the token to your bot client
token_rel_path = "../TOKEN.txt"

# Text file containing (preferably) a single command prefix character
cmd_prefix_rel_path = "../CMD_PREFIX.txt"

# Directory containing discord.py cogs
cogs_dir_rel_path = "./cogs"

# For use in commands that check for owner status
OWNER_IDS = {
    230003732836909056, # Raymond
    208718477240827905, # Julian
    522893218036187138, # Miranda
    810600609736163329, # Florence
    322193892260708352, # Ryan
    298223516262596608, # Anthony
    185164088479973394, # Justin
    534900930915729408 # Lawrence
}

# Your bot token
TOKEN = readTextFile(token_rel_path)

# Your bot's command prefix
COMMAND_PREFIX = readTextFile(cmd_prefix_rel_path)

# For use in temporary messages
DEL_DELAY = 3

# For use in error handlers
ERROR_TITLE = "Something went wrong."
NO_PERM_MSG = "You don't have permissions to do that."