import datetime as dt
import discord
from discord.ext import commands
from globals import *

class Moderator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=["purge"], hidden=True)
    async def clear(self, ctx, num:int, *, reason:str = None):
        if num < 1:
            await ctx.send("Enter a number greater than or equal to 1.")
        elif num == 1:
            await ctx.channel.purge(limit=num+1, reason=reason)
            await ctx.send("Message deleted.", delete_after=DEL_DELAY)
        else:
            await ctx.channel.purge(limit=num+1, reason=reason)
            await ctx.send(f"{num} messages deleted.", delete_after=DEL_DELAY)

    @clear.error
    async def clear_error(self, ctx, error):
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

    @commands.command(hidden=True)
    async def timeout(self, ctx, member:discord.Member, *time:str):
        days = 0; hours = 0; minutes = 0; seconds = 0
        for x in time:
            if time.lower().endswith("d"):
                days += int(x[:-1])
            elif time.lower().endswith("h"):
                hours += int(x[:-1])
            elif time.lower().endswith("m"):
                minutes += int(x[:-1])
            elif time.lower().endswith("s"):
                seconds += int(x[:-1])
        member.timeout(dt.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds))
        await ctx.send(f"{member.name} has been timed out for {days}D {hours}H {minutes}M {seconds}S")

async def setup(bot):
    await bot.add_cog(Moderator(bot))