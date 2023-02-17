from discord.ext import commands
from globals import *
from decimal import Decimal
import random

class CoinFlip(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Flips a coin. Can either be heads or tails.", aliases=["flip", "coin"])
    async def coinflip(self, ctx):
        # Calls a random float between 0 and 0.99 inclusive. Returns heads if 0 - 0.48 and tails if 0.49 - 0.99
        await ctx.send("{}".format("heads" if random.random() > 0.49 else "tails" ) )
    
    @coinflip.error
    async def add_error(self, ctx, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.BadArgument):
            await ctx.send("Something went wrong.")

async def setup(bot):
    await bot.add_cog(CoinFlip(bot))