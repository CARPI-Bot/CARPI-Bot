from discord.ext import commands
from globals import *
from decimal import Decimal
import discord
import datetime

class Repo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Returns a meddage that can be interacted with (clicked on) bringing a user to our GitHub Repo.")
    async def repo(self, ctx):
        embedVar = discord.Embed(title="Click Here to Redirect to the {} Repository".format(ctx.guild.get_member(1067560443444478034).name), url='https://github.com/Zen1124/tsdb', color=0x0099FF, timestamp=datetime.datetime.now())
        embedVar.set_footer(text='\u200bRepository link requested by ' + str(ctx.author.nick))
        await ctx.send(embed= embedVar)
    
    @repo.error
    async def repo_error(self, ctx, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.BadArgument):
            await ctx.send("Something went wrong.")

async def setup(bot):
    await bot.add_cog(Repo(bot))