from discord.ext import commands
from globals import *
from decimal import Decimal

class Kill(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Kills instances", aliases=["shutdown"])
    async def kill(self, ctx):
        # Terminates client
        await self.bot.close()
    
    @kill.error
    async def shut_error(self, ctx, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.BadArgument):
            await ctx.send("Something went wrong.")

async def setup(bot):
    await bot.add_cog(Kill(bot))