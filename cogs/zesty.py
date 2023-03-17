from discord.ext import commands
from globals import *
import random
import datetime
import discord

class Zesty(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(description='sus callout')
    async def sus(self, ctx, *time:str):
        person = random.randint(0, 9)
        await ctx.send(f"{ctx.guild.members[person].mention} is SUS")
        await ctx.guild.member.timeout(datetime.timedelta(0, 0, 1, 0))
        await ctx.send(f"{ctx.guild.members[person].mention} get timed out for 1 min")
    
    @commands.command(description='secret message someone')
    async def callout(self, ctx, members: commands.Greedy[discord.Member], *, msg='personal callout'):
        for x in members:
            if not x.dm_channel == None:
                await x.dm_channel.send(f"Secret message: {msg}")
                await ctx.send("Message sent!")
            else:
                await x.create_dm()
                await x.dm_channel.send(f"Secret message: {msg}")
                await ctx.send("Message sent!")
        await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(Zesty(bot))
