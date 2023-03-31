from discord.ext import commands
from globals import *
import random
import discord
import datetime

class AcademicCalendar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ### ACADEMIC CALENDAR SCRAPER ### 


async def setup(bot):
    await bot.add_cog(AcademicCalendar(bot))