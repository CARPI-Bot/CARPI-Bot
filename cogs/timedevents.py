import asyncio
import datetime as dt
from discord.ext import commands
from globals import *

async def sleep(num):
    try:
        await asyncio.sleep(num)
    except asyncio.CancelledError:
        raise

class TimedEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description = "timer <number> <second, minute, hour> <optional event description>")
    async def timer(self, ctx, *time):

        # if len(time) < 2:
        #     await ctx.send("Not enough arguments! Ex. ?timer 360 seconds")
        #     return

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

        # Timer confirmation message
        await ctx.send("A timer has been set for {}D {}H {}M {}S from now.".format(days, hours, minutes, seconds))
    
        #unit conversion
        seconds += days * 86400
        seconds += hours * 3600
        seconds += minutes * 60
        
        # sleep = asyncio.create_task(sleep(seconds))
        # try:
        #     await sleep
        # except asyncio.CancelledError:
        #     await ctx.send("Timer cancelled.")

        await asyncio.sleep(seconds)

        #if there's more than 2 arguments, ping the person with the event name
        # if len(args) > 2:
        #     event = ''.join(args [2:])
        #     await ctx.send("Time for {} {}".format(event, ctx.author.mention))
        #     return

        #otherwise just do a normal ping
        await ctx.send(f"Your timer is up, {ctx.author.mention}")

async def setup(bot):
     await bot.add_cog(TimedEvents(bot))