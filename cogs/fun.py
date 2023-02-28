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

    @commands.command(description='Starts a poll (args in quotes)')
    async def poll(self, ctx, name, option1, option2):
        embedVar = discord.Embed(title=f"{name}",
                    description="", color=0x336EFF)
        embedVar.add_field(name="Option 1", value=f"{option1}", inline=False)
        embedVar.add_field(name="Option 2", value=f"{option2}", inline=False)
        #embedVar.set_footer(text=f"{ctx.created_at}")
        await ctx.send(embed=embedVar)
        await ctx.message.delete()
    #Error handling not firing
    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Put arguments in quotes")
            await ctx.send("Command usage: [Title] [Option 1] [Option 2]")
    
    @commands.command(description= "rolls a dice and sends the result")
    async def diceroll(self, ctx, n=6):
        """Sends the result of a single n-sided dice roll."""

        if type(n) != int:
            await ctx.send("Please give an interger!")
            return

        # Initializes a list of values from 1 to 6 and randomly sends a single value
        outcomes = [i + 1 for i in range(n)]
        result = random.choice(outcomes)

        await ctx.send("You rolled a {:d}.".format(result))

async def setup(bot):
    await bot.add_cog(Fun(bot))