import datetime
from discord.ext import commands

class TimedEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot