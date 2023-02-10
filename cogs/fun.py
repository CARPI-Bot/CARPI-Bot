from discord.ext import commands
from globals import *
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Pings sender', alias=['hi'])
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}!")

async def setup(bot):
    await bot.add_cog(Fun(bot))