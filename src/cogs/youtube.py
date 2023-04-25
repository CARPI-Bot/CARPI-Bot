import discord
import googlesearch
from discord.ext import commands
from globals import *


class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ytsearch')
    async def youtube_search(self, ctx, *, query):
        search_results = list(googlesearch.search(f'{query} site:youtube.com/watch', num_results=1))
        if search_results:
            await ctx.send(search_results[0])
        else:
            await ctx.send(f"No search results found for '{query}' on YouTube.")

async def setup(bot):
    await bot.add_cog(Youtube(bot))