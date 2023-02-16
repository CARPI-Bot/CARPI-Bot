from discord.ext import commands
from globals import *
import random

class Zesty(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(description='sus callout')
    async def sus(self, ctx):
        person = random.randint(0, 9)
        await ctx.send(f"{ctx.guild.members[person].mention} is SUS")

async def setup(bot):
    await bot.add_cog(Zesty(bot))
