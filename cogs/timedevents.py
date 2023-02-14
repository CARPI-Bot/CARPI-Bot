import asyncio
import datetime as dt
import discord
from discord.ext import commands
from globals import *

class TimedEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description = 'timer <number> <second, minute, hour> <optional event description>')
    async def timer(self, ctx, *args):
        #list of all units of time
        units_of_time = [["s", "second", "seconds"], ["min", "mins", "minute,", "minutes"], ["h", "hr", "hrs", "hours"]]

        #error checking in case user inputs command wrong 
        if len(args) < 2:
            await ctx.send('Not enough arguments! Ex. ?timer 360 seconds')
            return

        #looping to set the correct unit of time 
        unit = ""
        for i in range(3):
            if args[1] in units_of_time[i]:
                unit = units_of_time[i][-1]
                break

        #setting the number of time
        num = int(args[0])

        #sending timer confirmation 
        await ctx.send('A timer has been set for {} {} from now '.format(num, unit))

        #unit conversion
        if unit == 'min' or unit == 'mins' or unit == 'minute' or unit == 'minutes':
            num *= 60
        elif unit == 'hr' or unit == 'hrs' or unit == 'hours':
            num *= 3600
        
        await asyncio.sleep(num)

        #if there's more than 2 arguments, ping the person with the event name
        if len(args) > 2:
            event = ''.join(args [2:])
            await ctx.send("Time for {} {}".format(event, ctx.author.mention))
            return
        #otherwise just do a normal ping
        await ctx.send("Your timer for {} {} has finished {}".format(args[0], args[1], ctx.author.mention))

async def setup(bot):
     await bot.add_cog(TimedEvents(bot))