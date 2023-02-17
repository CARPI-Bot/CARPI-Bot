import datetime as dt
import discord
from discord.ext import commands
from globals import *

class Moderator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(description="Deletes the last x number of messages in the channel", aliases=["purge"], hidden=True)
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

    @commands.command(description="Puts a user into timeout for a specified amount of time.", aliases=["mute", "silence"], hidden=True)
    async def timeout(self, ctx, member:discord.Member, *time:str):
        
        days = 0; hours = 0; minutes = 0; seconds = 0
        for element in time:
            if element.lower().endswith("d"):
                days += int(element[:-1])
            elif element.lower().endswith("h"):
                hours += int(element[:-1])
            elif element.lower().endswith("m"):
                minutes += int(element[:-1])
            elif element.lower().endswith("s"):
                seconds += int(element[:-1])
            else:
                raise commands.BadArgument
        
        # Fixes any overflowing time components
        if seconds >= 60:
            minutes += seconds // 60
            seconds %= 60
        if minutes >= 60:
            hours += minutes // 60
            minutes %= 60
        if hours >= 24:
            days += hours // 24
            hours %= 24

        await member.timeout(dt.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds))
        await ctx.send(f"{member.name} has been timed out for {days}D {hours}H {minutes}M {seconds}S")
    
    @timeout.error
    async def timeout_error(self, ctx, error):

        if isinstance(error, commands.BadArgument):
            await ctx.send(f"Usage: `{COMMAND_PREFIX}timeout <member> <days>d <hours>h <minutes>m <seconds>s`")
        else:
            await ctx.send(str(error))

    @commands.command(description="Removes timeout status from a user if they're currently timed out.", aliases=["untimeout"], hidden=True)
    async def timein(self, ctx, member:discord.Member):
        
        if member.is_timed_out():
            await member.timeout(dt.timedelta(seconds=0))
            await ctx.send(f"Removed timeout from {member.name}.")
        else:
            await ctx.send(f"{member.name} is not timed out.")
    
    @timein.error
    async def timein_error(self, ctx, error):
        if isinstance(commands.BadArgument):
            await ctx.send(f"Usage: `{COMMAND_PREFIX}timein <member>`")
        else:
            await ctx.send(str(error))


async def setup(bot):
    await bot.add_cog(Moderator(bot))