from discord.ext import commands
from globals import *
import discord
import urllib.parse, urllib.request, re

class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ### YOUTUBE SEARCHER ### 
    @commands.command()
    async def youtube(ctx, *, search):
        await ctx.send('Testing!')

async def setup(bot):
    await bot.add_cog(Youtube(bot))