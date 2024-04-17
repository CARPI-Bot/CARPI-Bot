import json
import logging
import sys
from pathlib import Path

import discord
from discord import Interaction
from discord.app_commands import AppCommandError
from discord.ext.commands import CommandError, Context


async def send_generic_error(
    ctx: Context | Interaction,
    error: CommandError | AppCommandError = None
) -> None:
    """
    Standard error message for any unhandled or unexpected command errors.
    Works with both discord.ext.commands and discord.app_commands frameworks.
    """
    embed = discord.Embed(
        title = ERROR_TITLE,
        description = "Unknown error. This is probably the devs' fault, sorry!",
        color = discord.Color.red()
    )
    if isinstance(ctx, Context):
        await ctx.send(embed=embed)
    else:
        try:
            await ctx.response.send_message(embed=embed)
        except:
            await ctx.followup.send(embed=embed)
    if error is not None:
        logging.error(
            msg = f"Error from command {ctx.command.name}",
            exc_info = True
        )

# For use in commands that check for owner status
OWNER_IDS = {
    230003732836909056, # Raymond
    298223516262596608, # Anthony
    310864184923652107, # Edwin
    455125448884748308, # Jack
}

# Base directory to search for relative paths from
BASE_DIR = Path(__file__).parent

try:
    with Path(__file__).with_name("config.json").open() as infile:
        CONFIG = json.load(infile)
except:
    print("Bad or missing config.json!")
    sys.exit(1)

# For use in error handlers
ERROR_TITLE = "Something went wrong"
NO_PERM_MSG = "You don't have permission to do that."
BAD_MEMBER_MSG = "Member not found. Nicknames and usernames are case sensitive, or" \
                 + "maybe you spelled it wrong?"
