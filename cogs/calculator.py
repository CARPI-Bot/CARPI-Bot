from discord.ext import commands
from globals import *

class Calculator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def add(self, ctx, num1:int, num2:int):
        await ctx.send(num1 + num2)

    @commands.command(aliases=["sub"])
    async def subtract(self, ctx, num1:int, num2:int):
        await ctx.send(num1 + num2)