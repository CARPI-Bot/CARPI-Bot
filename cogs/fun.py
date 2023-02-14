from discord.ext import commands
from globals import *
import random
import discord

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Pings sender', aliases=["hi","hey"])
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}!")

    @commands.command(description='Pings random member and calls them stinky')
    async def stinky(self, ctx):
        #Get random position of memberlist
        stinky = random.choice(ctx.guild.members)
        await ctx.send(f"{stinky.mention} is stinky!")

    @commands.command(description='Sends an anonymous message to intended user through bot')
    async def secret(self, ctx, members: commands.Greedy[discord.Member], *, msg='so secret'):
        for x in members:
            if not x.dm_channel == None:
                await x.dm_channel.send(f"Secret message: {msg}")
                await ctx.send("Message sent!")
            else:
                await x.create_dm()
                await x.dm_channel.send(f"Secret message: {msg}")
                await ctx.send("Message sent!")
        await ctx.message.delete()
    #Error handling not firing
    @secret.error
    async def secret_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Command usage: [user/users] [message]")
async def setup(bot):
    await bot.add_cog(Fun(bot))