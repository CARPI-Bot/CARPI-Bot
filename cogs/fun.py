from discord.ext import commands
from globals import *
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Pings sender', aliases=["hi","hey"])
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}!")

    
    @commands.command(description='Pings random member and calls them stinky')
    async def stinky(self, ctx):
        #Get random position of memberlist
        m = random.randint(0, 9)
        await ctx.send(f"{ctx.guild.members[m].mention} is stinky!")

async def setup(bot):
    await bot.add_cog(Fun(bot))