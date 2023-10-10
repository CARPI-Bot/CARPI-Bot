import asyncio
from globals import *
from time import sleep
from datetime import date, datetime

from discord.ext import commands
from cogs.calendar.academic_cal import events_from_webpage, getMonthAndDate

class AcadCal(commands.Cog) :
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(description="Prints the current month's calendar and events.",
                             aliases=["cal"])
    async def print_calendar(self, ctx):
        
        dates = events_from_webpage()
        calendar = getMonthAndDate(dates)


        # Create an emded for the message
        embedVar = discord.Embed(
            title=f"upcoming for october"
        )

        embedVar.add_field(
            name = datetime.now().month,
            value = calendar[0]
        )

        await ctx.send(embed=embedVar)
    
    @print_calendar.error
    async def print_calendar_error(self, ctx, error):
        print(error)

    
async def setup(bot):
    await bot.add_cog(AcadCal(bot))
