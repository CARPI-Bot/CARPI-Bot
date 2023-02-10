import datetime as dt
from discord.ext import commands

class TimedEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(TimedEvents(bot))