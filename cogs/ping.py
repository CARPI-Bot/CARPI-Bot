from discord.ext import commands
from globals import *
from decimal import Decimal
import discord
import random
import datetime

class Ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Gets the latentcy of the server")
    async def ping(self, ctx):
        # Retrieves the server latency in MS.
        embedVar = discord.Embed(title="Pong!", description="Your message was recieved in {}ms.".format(str(round(self.bot.latency * 1000) ) ), color=0x00C500, timestamp=datetime.datetime.now())
        embedVar.set_footer(text='\u200bPing checked by ' + str(ctx.author.nick))
        await ctx.send(embed= embedVar)
    
    @ping.error
    async def ping_error(self, ctx, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.BadArgument):
            await ctx.send("Something went wrong.")

async def setup(bot):
    await bot.add_cog(Ping(bot))