import platform
import os
import discord
from discord.ext import commands
from globals import *
from cogs import calculator

TOKEN = open("TOKEN.txt").read()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, owner_ids=OWNER_IDS, intents=intents)

@bot.event
async def on_ready():
    await bot.add_cog(calculator.Calculator(bot))
    await bot.add_cog(gavin.Gavin(bot))
    print(f"Logged in as {bot.user.name}#{bot.user.discriminator}")
    print(f"Python version {platform.python_version()}")
    print(f"Discord.py version {discord.__version__}")

@bot.command(aliases=["purge"])
async def clear(ctx, num:int, *, reason:str = None):
    if num < 1:
        await ctx.send("Enter a number greater than or equal to 1.")
    elif num == 1:
        await ctx.channel.purge(limit=num+1, reason=reason)
        await ctx.send("Message deleted.", delete_after=DEL_DELAY)
    else:
        await ctx.channel.purge(limit=num+1, reason=reason)
        await ctx.send(f"{num} messages deleted.", delete_after=DEL_DELAY)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Enter a valid integer.")
    # elif isinstance(error, commands.CheckFailure):
    #     await ctx.send("You don't have the 'Manage Messages' permission.")
    elif isinstance(error, commands.CommandInvokeError):
        error = error.original
        if isinstance(error, (discord.errors.HTTPException, discord.HTTPException)):
            await ctx.send("I don't have the 'Manage Messages' permission.")
    else:
        await ctx.send("Usage: `?clear [number of messages] [optional reason]`")

def main():
    bot.run(TOKEN)
    
if __name__ == "__main__":
    main()