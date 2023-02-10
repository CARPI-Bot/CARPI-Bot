import datetime as dt
from discord.ext import commands
from globals import *

class TimedEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage = ':) timer <number> <second[s], minute[s], hour[s]> <optional event description>')
    async def timer(self, ctx, *args):

        #error checking in case user inputs command wrong 
        if(len(args) < 2):
            await ctx.send('Not enough arguments! Ex. ?timer 360 seconds')
            return

        #setting the unit of time
        unit = ""

        #list of all units of time
        units_of_time = [['second', 'seconds'], ['minute', 'minutes'], ['hour', 'hours']]

        #looping to set the correct unit of time 
        for i in range(3):
            if args[i] in units_of_time[i]:
                unit = units_of_time[i][-1]
                break

        #setting the number of time
        num = args[0]

        #confirming the timer was set 
        await ctx.send('A timer has been set for {} {} from now ').format(num, unit)

        #converting to seconds if needed 
        if unit == "hour" or unit == "hours":
            num = num * 60 * 60
        elif unit == "minute" or unit == "minutes":
            num = num * 60
        
        await ctx.sleep(num)

        #if there's more than 2 arguments, ping the person with the event name
        if len(args) < 2:
            event = ''.join(args [2:])
            await ctx.send("Time for {} {}".format(event, ctx.author.mention))
            return
        
        #otherwise just do a normal ping
        await ctx.send("Your timer has finished {}".format(ctx.author.mention))

    async def setup(bot):
        await bot.add_cog(TimedEvents(bot))